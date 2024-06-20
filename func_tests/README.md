## TO RUN LOCALLY AGAINST DOCKER

You need to do these first steps one time to create a login token

```bash
cd sml_server/functest/pytest
python
```

```python
from sensiml import *
SensiML(server="localhost_docker", insecure=True)
exit()
```

After that you should be able to run the pytest without needing to do the login step again

py.test --rlocal=True --server=localhost_docker

#run a single test at a time locally
cd pytests_tests/python_core_functions
py.test --rlocal=True test_functions.py::test_fg_energy_total_energy_y_column --server=localhost_docker

py.test --html=report.html --rlocal=True --server=localhost_docker  --insecure=True pipeline_tests 
