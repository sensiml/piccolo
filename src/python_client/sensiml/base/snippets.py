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

class empty:
    pass


param_tabs = ",\n" + " " * 4 * 8


def function_help(func):
    filter_list = [
        "group_columns",
        "label_column",
        "ignore_columns",
        "passthrough_columns",
        "classifiers",
        "validation_methods",
    ]
    params = []
    for item in func.input_contract:
        key = item.get("name")
        value = item.get("default", None)
        key_type = item.get("type", None)
        options = item.get("options", None)
        if value is not None:
            if key_type == "str":
                params.append(f'"{key}": "{value}"')
            else:
                params.append(f'"{key}": {value}')

            if options is not None and key not in filter_list:
                values = map(lambda x: x["name"], options)
                params[-1] += ", #options: " + f"<{'/'.join(values)}>"
        elif options and key not in filter_list:
            values = map(lambda x: x["name"], options)
            params.append(f"\"{key}\": <{'/'.join(values)}>")
        elif (
            key_type in ["int", "float", "str", "numeric", "list", "dict"]
            and key not in filter_list
        ):
            params.append(f'"{key}": <{key_type}>')

    params.append("")

    if func.type == "Feature Generator":
        return """client.pipeline.add_feature_generator([{{'name':'{}', 'params':{{{}}}}}])""".format(
            func.name, param_tabs.join(params)
        )

    if func.type == "Feature Selector":
        return """client.pipeline.add_feature_selector([{{'name':'{}', 'params':{{{}}}}}], params={{'number_of_features':(int)}})""".format(
            func.name, param_tabs.join(params)
        )

    if func.type == "Augmentation":
        return """client.pipeline.add_augmentation(["name":"{}", "params":{{{}}}])""".format(
            func.name, param_tabs.join(params)
        )

    if func.type in ["Segmenter", "Transform", "Sampler"]:
        return """client.pipeline.add_transform("{}", params={{{}}})""".format(
            func.name, param_tabs.join(params)
        )

    if func.type == "Training Algorithm":
        return """client.pipeline.set_training_algorithm("{}", params={{{}}})""".format(
            func.name, param_tabs.join(params)
        )

    if func.type == "Validation Method":
        return """client.pipeline.set_validation_method("{}", params={{{}}})""".format(
            func.name, param_tabs.join(params)
        )

    if func.type == "Classifier":
        return """client.pipeline.set_classifier("{}", params={{{}}})""".format(
            func.name, param_tabs.join(params)
        )

    if func.type == "Regression":
        return """client.pipeline.set_regression("{}", params={{{}}})""".format(
            func.name, param_tabs.join(params)
        )

    return None


class hold_function:
    def __init__(self, func):
        self.func = func

    def create_function(self):
        try:
            docs = function_help(self.func)
        except:
            docs = "unable to generate this function."
        try:
            get_ipython().set_next_input(docs, replace=True)
        except:
            print(docs)

        return docs


class Snippets:
    def __init__(self, function_df, function_list):
        self._function_df = function_df
        self._function_list = function_list
        self._attach_types()

    def _attach_types(self):
        type_list = self._function_df.TYPE.unique()
        for func_type in type_list:
            if not func_type:
                continue

            if func_type == "Transform":
                for subtype in self._function_df[
                    self._function_df.TYPE == func_type
                ].SUBTYPE.unique():
                    setattr(
                        self,
                        subtype.replace(" ", "_")
                        if "Filter" in subtype
                        else subtype.replace(" ", "_") + "_Transform",
                        self._attach_functions(subtype=subtype),
                    )
            else:
                setattr(
                    self,
                    func_type.replace(" ", "_"),
                    self._attach_functions(func_type=func_type),
                )
        # setattr(self, 'Auto', self._attach_seeds())

    def _attach_functions(self, func_type=None, subtype=None):
        cls = empty()
        if subtype:
            funcs = self._function_df[self._function_df.SUBTYPE == subtype]
        else:
            funcs = self._function_df[self._function_df.TYPE == func_type]
        for func in funcs.NAME:
            # functions names starting with numbers not allowed, check for them here
            sfunc = func
            if sfunc[:1] in "0123456789":
                sfunc = "FG_" + func
            setattr(
                cls,
                sfunc.replace(" ", "_").replace("-", ""),
                hold_function(self._function_list[func]).create_function,
            )

        return cls


def get_group_columns(steps):
    for step in steps:
        inputs = step.get("inputs", None)
        if inputs:
            return inputs.get("group_columns")


def get_label_column(steps):
    for step in steps:
        if step.get("type", None) == "tvo":
            return step.get("label_column", None)


def pipeline_function_help(
    function_list,
    step,
    filter_list=[
        "group_columns",
        "label_column",
        "ignore_columns",
        "passthrough_columns",
        "classifiers",
        "validation_methods",
        "input_data",
        "return_segment_index",
    ],
):

    function_name = step.get("name", None)
    if function_name is None:
        function_name = step.get("function_name", None)
    if function_name is None:
        return None

    func = function_list[function_name]

    params = []
    for item in func.input_contract:
        key = item.get("name")
        if key not in filter_list:
            value = step["inputs"].get(key, None)
            if value is not None:
                if item.get("type", None) == "str":
                    params.append(f'"{key}":"{value}"')
                else:
                    params.append(f'"{key}":{value}')

    if func.type == "Feature Generator":
        return f"""{{'name':'{func.name}', 'params':{{{param_tabs.join(params)}}}}}"""

    if func.type == "Feature Selector":
        return f"""{{'name':'{func.name}', 'params':{{{param_tabs.join(params)}}}}}, """

    if func.type == "Augmentation":
        return """\n{}{{"name": "{}", "params": {{{}}}}},""".format(
            " " * 32, func.name, param_tabs.join(params)
        )

    if func.type in ["Segmenter", "Transform", "Sampler"]:
        return """client.pipeline.add_transform("{}", params={{{}}})""".format(
            func.name, param_tabs.join(params)
        )

    if func.type == "Training Algorithm":
        return """client.pipeline.set_training_algorithm("{}", params={{{}}})""".format(
            func.name, param_tabs.join(params)
        )

    if func.type == "Validation Method":
        return """client.pipeline.set_validation_method("{}", params={{{}}})""".format(
            func.name, param_tabs.join(params)
        )

    if func.type == "Classifier":
        return """client.pipeline.set_classifier("{}", params={{{}}})""".format(
            func.name, param_tabs.join(params)
        )

    if func.type == "Regression":
        return """client.pipeline.set_regression("{}", params={{{}}})""".format(
            func.name, param_tabs.join(params)
        )

    return None


def build_pipeline(function_list, steps):
    pipeline_steps = ["client.pipeline.reset()"]

    for step in steps:
        if step.get("type") == "generatorset":
            feature_generators = []
            for generator in step["set"]:
                feature_generators.append(
                    pipeline_function_help(function_list, generator)
                )
            pipeline_steps.append(
                """client.pipeline.add_feature_generator([{}])""".format(
                    ",\n{}".format(" " * 40).join(feature_generators)
                )
            )

        elif step.get("type") == "selectorset":
            feature_selectors = []
            for selector in step["set"]:
                feature_selectors.append(
                    pipeline_function_help(function_list, selector)
                )
            pipeline_steps.append(
                "client.pipeline.add_feature_selector([{}])"
                "".format("\n{}".format(" " * 40).join(feature_selectors))
            )

        elif step.get("type") == "augmentationset":
            data_augmentors = []
            for augmentor in step["set"]:
                data_augmentors.append(pipeline_function_help(function_list, augmentor))
            pipeline_steps.append(
                "client.pipeline.add_augmentation([{}])"
                "".format("{}".format(" " * 40).join(data_augmentors))
            )

        elif step.get("type") == "tvo":
            for key in ["classifiers", "validation_methods", "optimizers"]:
                if step[key]:
                    pipeline_steps.append(
                        pipeline_function_help(function_list, step[key][0])
                    )

            pipeline_steps.append(
                "client.pipeline.set_tvo({{'validation_seed':{}}})".format(
                    step.get("validation_seed", 0)
                )
            )

        elif step.get("type", None) == "featurefile":
            pipeline_steps.append(
                """client.pipeline.set_input_data("{}", data_columns={}, \n{}group_columns={},\n{}label_column="{}")""".format(
                    step.get("name", None),
                    step.get("data_columns", None),
                    " " * 40,
                    get_group_columns(steps),
                    " " * 40,
                    get_label_column(steps),
                )
            )

        elif step.get("type", None) == "query":
            pipeline_steps.append(
                """client.pipeline.set_input_query("{query_name}", use_session_preprocessor={use_session_preprocessor})""".format(
                    query_name=step.get("name", None),
                    use_session_preprocessor=step.get("use_session_preprocessor", True),
                )
            )

        elif step.get("type", None) == "datafile":
            pipeline_steps.append(
                """client.pipeline.set_input_data("{file_names}", group_columns={group_columns}, label_column="{label_column}")""".format(
                    file_names=step.get("name"),
                    group_columns=step.get("group_columns"),
                    label_column=step.get("label_column"),
                )
            )
        else:
            pipeline_steps.append(pipeline_function_help(function_list, step))

    return pipeline_steps


def generate_pipeline(function_list, steps, replace=True):
    pipeline_steps = build_pipeline(function_list, steps)

    if replace:
        pipeline_string = "\n\n".join([x for x in pipeline_steps if x])
        get_ipython().set_next_input(pipeline_string, replace=True)

    return pipeline_steps
