"""
Copyright 2017-2024 SensiML Corporation

This file is part of SensiML™ Piccolo AI™.

SensiML Piccolo AI is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

SensiML Piccolo AI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>.
"""

import json
import pprint
from collections import namedtuple

from datamanager.utils.snippets import build_pipeline
from django.conf import settings
from django.db.models import Q
from library.models import Transform


def get_execution_code(sandbox):
    output = []
    if sandbox.hyper_params:
        output.append(f"params = {pprint.pformat(sandbox.hyper_params)}")
        output.append("results, summary = client.pipeline.auto(auto_params=params)")
    else:
        output.append("results, summary = client.pipeline.execute()")

    return output


def generate_python_code(sandbox):
    function_list = Transform.objects.filter(
        Q(library_pack__team=sandbox.project.team) | Q(library_pack__isnull=True)
    )

    pipeline_code = "\n\n".join(build_pipeline(function_list, sandbox.pipeline))

    execution_code = "\n".join(get_execution_code(sandbox))

    template = f"""#%%[markdown]
## {settings.PYTHON_CLIENT_NAME} Python Pipeline

This code uses the {settings.PYTHON_CLIENT_NAME} Python SDK to create and execute the pipeline.

#%%
# Execute this cell if you haven't installed the Python SDK
!pip install {settings.PYTHON_CLIENT_NAME} -U

#%%[markdown]
## Setup Client

Import the Client and connect to your project and pipeline

#%%
from {settings.PYTHON_CLIENT_NAME.lower()} import Client

client = Client()
client.project="{sandbox.project.name}"
client.pipeline="{sandbox.name}"

#%%[markdown]
## Generate Pipeline

This programmatically generates the pipeline JSON to execute 

#%%
{pipeline_code}

client.pipeline.describe()

#%%[markdown]
## Execute Pipeline

Executes the pipeline and polls for the results.

#%%
{execution_code}

#%%[markdown]
## Summarize Results
    
#%%
results.summarize()

#%%[markdown]
## Helpful Functions

The Python SDK has a rich feature set for interacting with the Rest API's. Here are some helpful functions to get started. 

For more details see the documentation for the Python SDK API. 

```python
# list projects
client.project.list_projects()

# list pipelines
client.list_pipelines()

# get cached data from executed pipeline
client.pipeline.data(<step-index>, <page-index>)

# list models
client.project.list_knowledgepacks()

# list captures
client.list_captures()

# execute single pipeline
results, summary = client.pipeline.execute()

# run model against captured data 
model = client.get_knowledgepack(<uuid>)
model.recognize_signal(capture=<capture_name>)
```
"""

    return template


def generate_ipynb_code(sandbox):
    Cell = namedtuple("Cell", "cell_type cell_header len")
    MarkDownCell = Cell(
        cell_type="markdown", cell_header="[markdown]", len=len("[markdown]")
    )

    python_template = generate_python_code(sandbox)

    raw_cells = python_template.split("#%%")

    def get_cell_template(cell_type, text):
        return {
            "cell_type": cell_type,
            "execution_count": 0,
            "metadata": {},
            "outputs": [],
            "source": [text],
        }

    cells = []
    for cell in raw_cells:
        if MarkDownCell.cell_header in cell[: MarkDownCell.len]:
            cells.append(
                get_cell_template(MarkDownCell.cell_type, cell[MarkDownCell.len :])
            )
        else:
            cells.append(get_cell_template("code", cell))

    ipynb_template = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.9.10",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 4,
    }

    return json.dumps(ipynb_template)
