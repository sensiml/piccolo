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

import os

import pandas as pd


def check_function_string(path, filename, function_name, c_type="int32_t"):
    print(path, filename, function_name)
    with open(os.path.join(path, filename), "r") as fid:
        for line in fid.readlines():
            if c_type + " " + function_name + "(" in line:
                return True

    return False


def get_function_string(path, filename, function_name, c_type="int32_t"):
    print(path, filename, function_name)
    with open(os.path.join(path, filename), "r") as fid:
        for line in fid.readlines():
            if c_type + " " + function_name + "(" in line:
                return line.rstrip() + ";"

    raise Exception()


def generate_fg_algorithms_c(functions):
    template = """// {name}
void {c_function_name}_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {{
        input_params.data[i] = params[i];
    }}
    input_params.size = num_params;
    {c_function_name}(&kb_model, &input_columns, &input_params, out_array);
}}
"""

    algorithms = []
    for index in functions[functions["type"] == "Feature Generator"].index:
        if functions.loc[index]["has_c_version"]:
            algorithms.append(
                template.format(
                    c_function_name=functions.loc[index].loc["c_function_name"],
                    name=functions.loc[index].loc["name"],
                )
            )

    with open("templates/fg_algorithms.template.c", "r") as fid:
        f = fid.read()
        f += "\n".join(algorithms)

    with open("../src/fg_algorithms.c", "w") as out:
        out.write(f)


def generate_fg_algorithms_python(functions):
    template = """# {name}
libcd.{c_function_name}_w.restype = None
libcd.{c_function_name}_w.argtypes = [
    array_1d_int,
    array_1d_float,
    array_1d_float,
    c_int,
    c_int,
    c_int,
]


def {c_function_name}_w(in_array, out_array, params, num_cols, num_rows):
    return libcd.{c_function_name}_w(
        in_array, out_array, params, len(params), num_cols, num_rows
    )

"""

    algorithms = []

    for index in functions[functions["type"] == "Feature Generator"].index:
        if functions.loc[index]["has_c_version"]:
            algorithms.append(
                template.format(
                    c_function_name=functions.loc[index].loc["c_function_name"],
                    name=functions.loc[index].loc["name"],
                )
            )

    with open("templates/fg_algorithms.template.py", "r") as fid:
        f = fid.read()
        f += "\n".join(algorithms)

    with open("../../server/library/core_functions/fg_algorithms.py", "w") as out:
        out.write(f)


def generate_fg_library_python(functions):
    template_single = """
def {c_function_name}(input_data, columns, {input_parameters}):

    return fg_algorithms.run_feature_generator_c(
        input_data, 
        columns,
        {name}, 
        {c_parameters},
        fg_algorithms.{c_function_name}_w
    )

"""

    template_single_multi_columns = """
def {c_function_name}(input_data, columns, {input_parameters}):

    return fg_algorithms.run_feature_generator_c_multiple_columns(
        input_data, 
        columns,
        {name}, 
        {c_parameters},
        fg_algorithms.{c_function_name}_w
    )

"""

    template_family = """
def {c_function_name}(input_data, columns, {input_parameters}):

    result_names = ["{name}_{{0:06}}".format(index) for index in range({output_length})]

    return fg_algorithms.run_feature_generator_c(
        input_data, 
        columns,
        result_names, 
        {c_parameters},
        fg_algorithms.{c_function_name}_w
    )

"""

    template_family_multi_columns = """
def {c_function_name}(input_data, columns, {input_parameters}):

    result_names = ["{name}_{{0:06}}".format(index) for index in range({output_length})]

    return fg_algorithms.run_feature_generator_c_multiple_columns(
        input_data, 
        columns,
        result_names, 
        {c_parameters},
        fg_algorithms.{c_function_name}_w
    )
"""

    algorithms = []

    for index in functions[functions["type"] == "Feature Generator"].index:
        if functions.loc[index]["has_c_version"]:
            algorithms.append(
                template.format(
                    c_function_name=functions.loc[index].loc["c_function_name"],
                    name=functions.loc[index].loc["name"],
                )
            )

    with open("templates/fg_algorithms.template.py", "r") as fid:
        f = fid.read()
        f += "\n".join(algorithms)

    with open("../../server/library/core_functions/fg_algorithms.py", "w") as out:
        out.write(f)


def generate_pywrapper_makefile(functions):
    c_files = []
    for index in functions[functions["type"] == "Feature Generator"].index:
        if functions.loc[index]["has_c_version"]:
            c_files.append(functions.loc[index].loc["c_file_name"] + " \\")

    with open("templates/Makefile.template", "r") as fid:
        f = fid.read()
        f = f.replace("// FILL_SRC_FILES", "\n".join(c_files))

    with open("../pywrapper/Makefile", "w") as out:
        out.write(f)


def generate_kbalgorithms_header_file(functions):
    path = "../src/"
    algorithms = {
        "sensor_filters": [],
        "sensor_transforms": [],
        "segmenters": [],
        "segment_transforms": [],
        "segment_filters": [],
        "feature_generators": [],
        "feature_vector_transforms": [],
    }

    for index in functions[functions["has_c_version"] == True].index:
        name = functions.loc[index].loc["name"]
        c_file = functions.loc[index].loc["c_file_name"]
        c_function_name = functions.loc[index].loc["c_function_name"]
        function_type = functions.loc[index].loc["type"]
        function_subtype = functions.loc[index].loc["subtype"]
        if not c_file:
            continue

        if function_type == "Transform" and function_subtype == "Sensor":
            algorithms["sensor_transforms"].append(
                get_function_string(path, c_file, c_function_name)
            )

        if function_type == "Transform" and function_subtype == "Sensor Filter":
            algorithms["sensor_filters"].append(
                get_function_string(path, c_file, c_function_name)
            )

        if function_type == "Transform" and function_subtype == "Segment":
            algorithms["segment_transforms"].append(
                get_function_string(path, c_file, c_function_name)
            )

        if function_type == "Transform" and function_subtype == "Segment Filter":
            algorithms["segment_filters"].append(
                get_function_string(path, c_file, c_function_name)
            )
            algorithms["segment_filters"].append(
                get_function_string(
                    path, c_file, "reset_" + c_function_name, c_type="void"
                )
            )

            if check_function_string(
                path, c_file, c_function_name + "_init", c_type="int32_t"
            ):
                algorithms["segment_filters"].append(
                    get_function_string(
                        path, c_file, c_function_name + "_init", c_type="int32_t"
                    )
                )

        if function_type == "Segmenter":
            algorithms["segmenters"].append(
                get_function_string(path, c_file, c_function_name)
            )
            algorithms["segmenters"].append(
                get_function_string(
                    path, c_file, c_function_name + "_init", c_type="void"
                )
            )

        if function_type == "Feature Generator":
            algorithms["feature_generators"].append(
                get_function_string(path, c_file, c_function_name)
            )

        if function_type == "Transform" and function_subtype == "Feature Vector":
            algorithms["feature_vector_transforms"].append(
                get_function_string(path, c_file, c_function_name)
            )

    with open("templates/kbalgorithms.template.h", "r") as fid:
        f = fid.read()
        for key, text in algorithms.items():
            f = f.replace("// FILL_{}".format(key.upper()), "\n".join(text))

    with open("../include/kbalgorithms.h", "w") as out:
        out.write(f)


def generate_fg_library_file(functions):
    algorithms = {
        "sensor_filters": [],
        "sensor_transforms": [],
        "segmenters": [],
        "segment_transforms": [],
        "segment_filters": [],
        "feature_generators": [],
        "feature_vector_transforms": [],
    }

    for function in functions:
        if not function.has_c_version:
            continue

        if function.type != "Feature Generator":
            continue

        name = functions.name
        c_file = function.c_file_name
        c_function_name = function.c_function_name
        input_contact = function.input_contract
        output_contract = function.input_contract

        algorithms["feature_generators"].append(
            get_function_string(path, c_file, c_function_name)
        )

    with open("templates/fg_library.template.py", "r") as fid:
        f = fid.read()
        f = f.replace("// FILL_FG_LIBRARY_CALLS", "\n".join(c_files))

    with open("../pywrapper/fg_library.py", "w") as out:
        out.write(f)


if __name__ == "__main__":
    # gather all feature generators

    import pandas as pd
    from yaml import safe_load

    def get_function_df(file_path):
        with open(file_path, "r") as f:
            yml = safe_load(f)

        M = []
        for i in yml:
            M.append(i.pop("fields"))
        df = pd.DataFrame(M).fillna(False)

        return df

    df = get_function_df("../../server/library/fixtures/functions_prod.yml")
    df_develop = get_function_df("../../server/library/fixtures/functions_dev.yml")

    df = pd.concat([df, df_develop]).reset_index(drop=True)

    generate_fg_algorithms_c(df)
    generate_fg_algorithms_python(df)
    generate_pywrapper_makefile(df)
    generate_kbalgorithms_header_file(df)
    # generate_fg_library_file(df)
