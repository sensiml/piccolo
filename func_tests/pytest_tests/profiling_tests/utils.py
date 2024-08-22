from _pytest.mark import param


def get_longest_ouptput(platform, application):
    app = platform.applications[application]
    outputs = app["supported_outputs"]
    size = 0
    use = None
    for out in outputs:
        if len(out) > size:
            size = len(out)
            use = out

    return use


def generate_configuration_parameters(dsk):
    """use this to generate the paramterers for download all v2"""
    configurations = []
    for platform in dsk.platforms_v2.platform_list:

        if len(platform.platform_versions) == 0:
            supported_versions = [""]
        else:
            supported_versions = platform.platform_versions

        for version in supported_versions:
            for processor in platform.processors:
                for compiler in platform.supported_compilers:
                    for application in platform.applications.keys():
                        config = platform.get_config(debug=True)
                        config["target_processor"] = processor.uuid
                        config["target_compiler"] = compiler.uuid

                        config["float_options"] = processor.float_options.get(
                            platform.default_selections.get("float", ""), ""
                        )
                        config["application"] = application
                        config["output_options"] = get_longest_ouptput(
                            platform, application
                        )
                        config["platform.can_build_binary"] = platform.can_build_binary
                        config["selected_platform_version"] = version
                        config["platform.name"] = platform.name
                        config["processor.display_name"] = processor.display_name
                        config["compiler.name"] = compiler.name
                        config["compiler.compiler_version"] = compiler.compiler_version
                        config["processor.profiling_enabled"] = (
                            processor.profiling_enabled
                        )

                        configurations.append(config)

    return [
        (
            configurations[i]["platform.name"]
            + " "
            + configurations[i]["selected_platform_version"],
            configurations[i],
        )
        for i in range(len(configurations))
    ]


def generate_binary_only_configuration_parameters(dsk):
    """
    use this function to generate the parameters for the tf download

    """
    configurations = []
    for platform in dsk.platforms_v2.platform_list:

        if len(platform.platform_versions) == 0:
            supported_versions = [""]
        else:
            supported_versions = platform.platform_versions

        for version in supported_versions:
            for processor in platform.processors:
                for compiler in platform.supported_compilers:
                    for application in platform.applications.keys():
                        config = platform.get_config(debug=True)
                        config["target_processor"] = processor.uuid
                        config["target_compiler"] = compiler.uuid

                        config["float_options"] = processor.float_options.get(
                            platform.default_selections.get("float", ""), ""
                        )
                        config["application"] = application
                        config["output_options"] = get_longest_ouptput(
                            platform, application
                        )
                        config["platform.can_build_binary"] = platform.can_build_binary
                        config["selected_platform_version"] = version
                        config["platform.name"] = platform.name
                        config["processor.display_name"] = processor.display_name
                        config["compiler.name"] = compiler.name
                        config["compiler.compiler_version"] = compiler.compiler_version
                        config["processor.profiling_enabled"] = (
                            processor.profiling_enabled
                        )

                        if platform.can_build_binary:
                            configurations.append(config)

    return [
        (
            configurations[i]["platform.name"]
            + " "
            + configurations[i]["selected_platform_version"],
            configurations[i],
        )
        for i in range(len(configurations))
    ]


profile_parameter_configuration = (
    [
        (
            "Arduino Nano33 BLE Sense ",
            {
                "target_platform": "aaf098cb-7a11-4653-b1d3-e71800610208",
                "test_data": "",
                "debug": True,
                "output_options": ["Serial", "BLE"],
                "application": "AI Model Runner",
                "target_processor": "cafbed02-09b3-494e-8c07-966fe71e9727",
                "target_compiler": "7c98c2fa-a819-40a0-98f8-a60cc04130db",
                "float_options": "-mfloat-abi=softfp -mfpu=fpv4-sp-d16",
                "selected_platform_version": "nrf52",
                "platform.can_build_binary": True,
                "platform.name": "Arduino Nano33 BLE Sense",
                "processor.display_name": "Cortex M4",
                "compiler.name": "GNU Arm Embedded (none-eabi)",
                "compiler.compiler_version": "8.2.1",
                "processor.profiling_enabled": True,
            },
        ),
    ],
)

subtype_model_call_configuration = (
    [
        ("Time", {"sample_rate": 100}),
        ("Frequency", {"sample_rate": 100}),
        ("Rate of Change", {}),
        ("Energy", {}),
        ("Statistical", {}),
        ("Physical", {"sample_rate": 100}),
        ("Area", {"sample_rate": 100, "smoothing_factor": 9}),
        ("Amplitude", {"smoothing_factor": 9}),
    ],
)
