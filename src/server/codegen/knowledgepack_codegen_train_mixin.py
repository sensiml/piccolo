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

from codegen.utils import c_line


class TrainMixin(object):
    def create_case_fill_template(self, models_data, model_fill):
        output_str = ""
        model_fill["NULL"] = "ret = 0;"
        for index, model in enumerate(models_data):
            output_str += c_line(1, "case({}):".format(index))
            output_str += c_line(
                2,
                model_fill.get(
                    model["classifier_config"].get("classifier", "NULL"), "ret=0;"
                ),
            )
            output_str += c_line(2, "break;")

        return [output_str]

    def create_case_fill_template_with_retrain(self, models_data, model_fill):
        output_str = ""
        model_fill["NULL"] = "ret = 0;"
        for index, model in enumerate(models_data):
            output_str += c_line(1, "case({}):".format(index))
            if model["classifier_config"].get("reinforcement_learning", False):
                output_str += c_line(
                    2,
                    model_fill.get(
                        model["classifier_config"].get("classifier", "NULL"), "ret=0;"
                    ),
                )
            else:
                output_str += c_line(2, "ret = 0;")

            output_str += c_line(2, "break;")

        return [output_str]

    def create_case_fill_template_classifier_type(self, models_data, model_fill):
        output_str = ""
        model_fill["NULL"] = "ret = 0;"

        model_types = set()
        for index, model in enumerate(models_data):
            model_types.add(
                (
                    self.get_classifier_type_map(
                        models_data[index]["classifier_config"]
                    ),
                    model["classifier_config"].get("classifier", "NULL"),
                )
            )

        for classifier_type, model_type in sorted(list(model_types)):
            output_str += c_line(1, "case({}):".format(classifier_type))
            output_str += c_line(2, model_fill.get(model_type, "ret = 0;"))
            output_str += c_line(2, "break;")

        return [output_str]

    def create_kb_flush_model(self, models_data):
        model_fill = {}
        model_fill["PME"] = "pme_flush_model(kb_models[model_index].classifier_id);"

        return self.create_case_fill_template_classifier_type(models_data, model_fill)

    def create_kb_get_model_header(self, models_data):
        model_fill = {}
        model_fill["PME"] = (
            "pme_model_header->number_patterns = pme_get_number_patterns(kb_models[model_index].classifier_id);\n"
            + "pme_model_header->pattern_length = kb_models[model_index].pfeature_vector->size;"
        )

        return self.create_case_fill_template_classifier_type(models_data, model_fill)

    def create_kb_get_model_pattern(self, models_data):
        model_fill = {}
        model_fill["PME"] = (
            "pme_return_pattern(model_index, pattern_index, pme_pattern);"
        )

        return self.create_case_fill_template_classifier_type(models_data, model_fill)

    def create_kb_add_last_pattern(self, models_data):
        model_fill = {}
        model_fill["PME"] = (
            "ret = pme_add_new_pattern(kb_models[model_index].classifier_id, (uint8_t*)kb_models[model_index].pfeature_vector->data, category, influence);"
        )
        model_fill["Decision Tree Ensemble"] = "ret = 0;"
        model_fill["Boosted Tree Ensemble"] = "ret = 0;"
        model_fill["Bonsai"] = "ret = 0;"
        model_fill["TF Micro"] = "ret = 0;"
        model_fill["TensorFlow Lite for Microcontrollers"] = "ret = 0;"

        return self.create_case_fill_template(models_data, model_fill)

    def create_kb_add_custom_pattern(self, models_data):
        model_fill = {}
        model_fill["PME"] = (
            "ret = pme_add_new_pattern(kb_models[model_index].classifier_id, feature_vector, category, influence);"
        )

        return self.create_case_fill_template(models_data, model_fill)

    def create_kb_retrain_model(self, models_data):
        model_fill = {}
        model_fill["PME"] = (
            "pme_rebalance_patterns(kb_models[model_index].classifier_id);"
        )

        return self.create_case_fill_template_with_retrain(models_data, model_fill)

    def create_kb_score_model(self, models_data):
        model_fill = {}
        model_fill["PME"] = (
            "pme_score_pattern(kb_models[model_index].classifier_id, (uint8_t*)kb_models[model_index].pfeature_vector->data, category);"
        )

        return self.create_case_fill_template_with_retrain(models_data, model_fill)

    def create_kb_print_model_score(self, models_data):
        model_fill = {}
        model_fill["PME"] = (
            "pme_print_model_scores(kb_models[model_index].classifier_id);"
        )

        return self.create_case_fill_template_with_retrain(models_data, model_fill)
