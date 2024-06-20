import json
import os
import shutil
import time
import zipfile

import pytest
import yaml
from sensiml.profile import ProfileParser

from utils import profile_parameter_configuration, subtype_model_call_configuration

cost_file_path = os.path.abspath(r"../../server/library/fixtures/function_costs.yml")
function_file_path = os.path.abspath(
    r"../../server/library/fixtures/functions_prod.yml"
)


class PipelineFailedException(Exception):
    pass


def run_profile(com_port="/dev/ttyACM0", baud=921600, run_count=100, json_path=""):
    global parser
    parser = ProfileParser(
        json_path=json_path, port=com_port, num_msgs=run_count, baud=baud
    )
    parser.run()


def compile_new_nano33(lib_path, sdk_base_dir, com_port="/dev/ttyACM0"):
    kplib_dir = f"{sdk_base_dir}/lib/sensiml/"
    app_src_dir = f"{sdk_base_dir}/src/"
    saved_directory = os.path.abspath(os.curdir)
    try:
        shutil.rmtree("tmp", ignore_errors=True)
        os.mkdir("tmp")
        with zipfile.ZipFile(lib_path, "r") as zip_ref:
            x = zip_ref.infolist()
            zip_ref.extractall(path="tmp")
    except:
        return False
    try:
        shutil.copy("tmp/knowledgepack/libsensiml/libsensiml.a", kplib_dir)
        shutil.copy("tmp/knowledgepack/libsensiml/kb_typedefs.h", kplib_dir)
        shutil.copy("tmp/knowledgepack/libsensiml/kb_debug.h", kplib_dir)
        shutil.copy("tmp/knowledgepack/libsensiml/kb.h", kplib_dir)
        shutil.copy("tmp/knowledgepack/libsensiml/kb_defines.h", kplib_dir)
        shutil.copy("tmp/knowledgepack/libsensiml/model.json", kplib_dir)
        shutil.copy("tmp/knowledgepack/libsensiml/model_json.h", kplib_dir)
        shutil.copy(
            "tmp/knowledgepack/knowledgepack_project/sml_recognition_run.cpp",
            app_src_dir,
        )

        os.chdir(sdk_base_dir)
        if os.system("pio run -e nano33ble -t clean") != 0:
            print("Couldn't Clean")
            raise Exception("Failed to clean")
        if os.system("pio run -e nano33ble") != 0:
            print("Couldn't Build")
            raise Exception("Failed to build")
        if (
            os.system(
                "pio run -e nano33ble -t upload --upload-port {}".format(com_port)
            )
            != 0
        ):
            print("Couldn't Upload")
            raise Exception("Failed to upload")
        os.chdir(saved_directory)
    except:
        return False
    finally:
        shutil.rmtree("tmp", ignore_errors=True)
        os.chdir(saved_directory)
    return True


def run_profiles_nano33(zip_name, sdk_dir, port, baud, run_count=100):
    model_desc = f"{sdk_dir}/lib/sensiml/model.json"
    global parser
    lib_path = os.path.abspath(zip_name)

    if compile_new_nano33(lib_path, sdk_base_dir=sdk_dir, com_port=port):
        time.sleep(10)
        run_profile(com_port=port, run_count=run_count, baud=baud, json_path=model_desc)
        with open(lib_path[:-4] + ".yml", "w") as out:
            out.write(parser.to_yaml())
        return True
    else:
        print("Failed to build for " + lib_path)
        return False


download_zips = list()


@pytest.fixture(scope="session")
def session_configs():
    capture_configs = {
        "Arduino Nano33 BLE Sense": {
            "name": "Nano33 BLE Sense",
            "version": 3,
            "plugin_uuid": "3a11f17d-1ecc-4086-9526-da9ef2fc6417",
            "protocol_uuid": "5b2ffd03-7793-4f46-a91b-b515f1e4c837",
            "capture_sources": [
                {
                    "name": "Motion",
                    "part": "LSM9DS1",
                    "sensors": [
                        {
                            "type": "Accelerometer",
                            "sensor_id": 0,
                            "parameters": [],
                            "column_count": 3,
                            "column_names": [],
                            "can_live_stream": False,
                        },
                        {
                            "type": "Gyroscope",
                            "sensor_id": 0,
                            "parameters": [],
                            "column_count": 3,
                            "column_names": [],
                            "can_live_stream": False,
                        },
                    ],
                    "sample_rate": 119,
                    "sensor_combinations": [],
                }
            ],
            "is_little_endian": True,
            "stack_ram_defaults": os.path.join(
                os.path.dirname(__file__), "data", "arm_gcc_defaults.json"
            ),
            "processor": "241a03d2-3e13-4087-9d7b-07a3f96e6dff",
        }
    }

    return capture_configs


def check_result(dsk, r):
    if r is None:
        dsk.pipeline.stop_pipeline()
        raise PipelineFailedException("Pipeline Failed While Running")

    return True


def check_success_failure(success, failed):

    if failed:
        failed_string = ""
        success_string = ""

        for f in failed:
            if f[3] == "binary_profile":
                print("BINARY PROFILE FAILED PLATFORMS")
                print(f)
                failed_string += "binary_profile,  "

        for f in failed:
            if f[3] == "library_profile":
                print("LIBRARY PROFILE FAILED PLATFORMS")
                print(f)
                failed_string += "library_profile,  "

        for s in success:
            if s[3] == "binary_profile":
                print("BINARY PROFILE SUCCESS PLATFORMS")
                print(s)
                success_string += "binary_profile,  "

        for s in success:
            if s[3] == "library_profile":
                print("LIBRARY PROFILE SUCCESS PLATFORMS")
                print(s)
                success_string += "library_profile,  "

        result_string = "failed: " + failed_string + "  success:" + success_string

        raise Exception(
            "Ran {num_run} failed {num_failed} - {result_string}".format(
                num_run=len(success) + len(failed),
                num_failed=len(failed),
                result_string=result_string,
            )
        )


def print_summary(config, download_type):
    print("\n##################################")
    print("Download {}, debug: {}".format(download_type, config["debug"]))
    print(
        "Platform:",
        config["platform.name"],
        "Processor Name:",
        config["processor.display_name"],
        "Compiler:",
        "{} {}".format(config["compiler.name"], config["compiler.compiler_version"]),
        "Application: ",
        config["application"],
        "Profiling:",
        config["processor.profiling_enabled"],
    )

    print("###################################\n")


def dsk_model(ClientConnection, DataDir, capture_configs, subtype, params):

    import random

    import pandas as pd

    dsk = ClientConnection
    project_name = "Test_Project_{}".format(random.randint(0, 10000))
    prj = dsk.projects.get_project_by_name(project_name)

    # Delete the project if it exists
    if prj is not None:
        prj.delete()

    dsk.project = project_name
    dsk.pipeline = "TestPipeline"

    for k, v in capture_configs.items():
        cc = dsk.project.capture_configurations.create_capture_configuration(
            name=k, configuration=v
        )
        capture_configs[k]["created_uuid"] = cc.uuid

    df = pd.read_csv(
        "{}/kbbasics/activities_combinedSignalsWithLabel_tiny.csv".format(DataDir)
    )
    df = df.rename(columns={"Class": "Activity"})
    sensor_columns = ["AccelerometerX", "AccelerometerY", "AccelerometerZ"]
    df.head()

    dsk.pipeline.set_columns(data_columns=sensor_columns)

    dsk.upload_dataframe("grid_dataframe1", df, force=True)

    scall = {"subtype_call": f"{subtype}", "params": params}
    dsk.pipeline.reset()
    dsk.pipeline.set_input_data(
        "grid_dataframe1.csv",
        data_columns=sensor_columns,
        group_columns=["Subject", "Activity"],
        label_column="Activity",
    )  # , force=True)

    dsk.pipeline.add_transform("Windowing", params={"window_size": 200, "delta": 200})

    dsk.pipeline.add_feature_generator(
        [scall], function_defaults={"columns": sensor_columns}
    )
    dsk.pipeline.add_transform("Min Max Scale")

    dsk.pipeline.set_validation_method(
        "Stratified K-Fold Cross-Validation", params={"number_of_folds": 3}
    )
    dsk.pipeline.set_classifier(
        "PME", params={"classification_mode": "RBF", "distance_mode": "L1"}
    )
    dsk.pipeline.set_training_algorithm(
        "Hierarchical Clustering with Neuron Optimization",
        params={"number_of_neurons": 30, "cluster_method": "DLHC"},
    )
    dsk.pipeline.set_tvo({"validation_seed": 1})

    r, s = dsk.pipeline.execute()

    print(r)
    print(s)

    try:
        assert check_result(dsk, r)
        model = r.configurations[0].models[0].knowledgepack
    except:
        dsk.project.delete()
        raise Exception(r)
    model.save(f"{subtype}_profile")
    return dsk, model, capture_configs


def validate_results(res, config, path_or_err, download_type, success, failed):
    if res is False:
        print(config["platform.name"], res, path_or_err)
        failed.append((config["platform.name"], path_or_err, config, download_type))
    else:
        success.append((config["platform.name"], path_or_err, config, download_type))

    return success, failed


def get_time_profile_data(time_profiles):
    with open(function_file_path, "r") as ff:
        functions = yaml.safe_load(ff.read())
    profile_data = dict()
    for tp in time_profiles:
        with open(tp, "r") as y:
            prof = yaml.safe_load(y.read())
            prof.pop("FeatureTimePerInference")
            prof.pop("ClassifierAverageTime")
            tmp = prof["FeatureCyclesPerInference"][0].copy()
            prof["FeatureCyclesPerSample"] = list()
            prof["FeatureCyclesPerSample"].append(dict())
            for pprint_f_name, v in tmp.items():
                for func in functions:
                    if func["fields"]["name"] == pprint_f_name:
                        prof["FeatureCyclesPerSample"][0][
                            func["fields"]["c_function_name"]
                        ] = int(v / 200)
        profile_data.update(prof["FeatureCyclesPerSample"][0])
    return profile_data


def update_profile_costs_file(profile_data, default_costs, config, session_configs):

    with open(cost_file_path, "r") as existing:
        existing_func_costs = yaml.load(existing)

    costs_list = (
        default_costs
        if (existing_func_costs is None or len(existing_func_costs) == 0)
        else existing_func_costs
    )

    selected_processor = session_configs[config["platform.name"]]["processor"]
    for function_name, cycle_count in profile_data.items():
        existing_func = next(
            filter(
                lambda ef: ef["fields"]["c_function_name"] == function_name,
                costs_list,
            ),
            None,
        )
        if existing_func is None:
            default_func = next(
                filter(
                    lambda ef: ef["fields"]["c_function_name"] == function_name,
                    default_costs,
                ),
                None,
            )
            if default_func is not None:
                default_func["fields"]["processor"] = selected_processor
                default_func["fields"]["cycle_count"] = cycle_count
                costs_list.append(default_func)
        else:
            existing_proc = existing_func["fields"].get("processor", None)
            if existing_proc is None:
                existing_func["fields"]["processor"] = session_configs[
                    config["platform.name"]
                ]["processor"]
                existing_func["fields"]["cycle_count"] = cycle_count
            else:
                # profiling with new processor UUID
                new_func = existing_func.copy()
                new_func["fields"]["processor"] = session_configs[
                    config["platform.name"]
                ]["processor"]
                new_func["fields"]["cycle_count"] = cycle_count
                costs_list.append(new_func)

    with open(cost_file_path, "w") as fc:
        fc.write(yaml.dump(costs_list, indent=4))


@pytest.mark.parametrize("index,config", *profile_parameter_configuration)
@pytest.mark.parametrize("subtype,params", *subtype_model_call_configuration)
def test_profile_downloads_on_device(
    index,
    config,
    ClientConnection,
    DataDir,
    sdk_dir,
    device_port,
    device_baud,
    subtype,
    params,
    session_configs,
):
    dsk, model, capture_configs = dsk_model(
        ClientConnection, DataDir, session_configs, subtype, params
    )

    failed = []
    success = []

    config["debug"] = True
    output_name = ""
    config["kb_description"] = {"TestModel": {"uuid": model.uuid, "source": "Custom"}}
    if config["platform.name"] in capture_configs.keys():
        config["kb_description"]["TestModel"]["source"] = capture_configs[
            config["platform.name"]
        ]["created_uuid"]

        print_summary(config, "library_profile")
        config["profile"] = True
        config["profile_iterations"] = 10
        pn = config["platform.name"]
        output_name = f"{model.name}_{pn}.zip".lower().replace(" ", "_")
        path_or_err, res = model.download_library_v2(config=config, save_as=output_name)
        success, failed = validate_results(
            res, config, path_or_err, "library_profile", success, failed
        )
        config["profile"] = False

    try:
        if res is False:
            model.get_build_log(
                save_as="library_profile"
                + "_"
                + config["platform.name"]
                + "_"
                + config["compiler.name"]
                + "_"
                + config["compiler.compiler_version"]
                + "_"
                + config["processor.display_name"]
                + ".testprofiling.log"
            )
        else:
            download_zips.append(output_name)
    except:
        pass

    check_success_failure(success, failed)
    time_profiles = list()
    for dz in download_zips:
        result = run_profiles_nano33(
            dz, sdk_dir, device_port, device_baud, run_count=100
        )
        if result:
            time_profiles.append(dz[:-4] + ".yml")

    with open(
        os.path.abspath(capture_configs[config["platform.name"]]["stack_ram_defaults"]),
        "r",
    ) as json_defaults:
        default_costs = json.load(json_defaults)

    profile_data = get_time_profile_data(time_profiles)

    update_profile_costs_file(profile_data, default_costs, config, session_configs)
