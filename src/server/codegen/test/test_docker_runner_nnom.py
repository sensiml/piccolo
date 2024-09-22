import json
import os
import zipfile
import shutil
import codegen.knowledgepack_model_graph_mixin as kp_cg
import pandas as pd
import pytest
from codegen.codegen_gcc_generic import GCCGenericCodeGenerator
from datamanager.knowledgepack import get_generator
from datamanager.models import KnowledgePack, Project, Sandbox, Team, TeamMember
from library.models import CompilerDescription, ProcessorDescription
from codegen.docker_runner import get_docker_runner
from codegen.codegen_platform_mapper import KnowledgePackPlatformMapper
import uuid
pytestmark = pytest.mark.django_db  # All tests use db

TEAM_NAME = "SensimlDevTeam"


def test_docker_runner_nnom(
    knowledgepacks, platformsv2_setup, x86_device_config
):
    # device_config = {"target_platform": 4, "debug": True, "sample_rate": 100}

    device_config = x86_device_config


# Generate a UUID

    root_dir="/home/cknorow/test"
    new_uuid= "9733ecc3-d3c2-43f3-b396-899f0f968157"
    if not os.path.exists(root_dir):
        os.mkdir(root_dir)        
    if not os.path.exists(os.path.join(root_dir,new_uuid)):
        os.mkdir(os.path.join(root_dir,new_uuid))        

    task_id='test'
    debug='p'
    pm = KnowledgePackPlatformMapper("26eef4c2-6317-4094-8013-08503dcd4bc5", device_config=device_config)
    target_arch=""
    dockerRunner = get_docker_runner(docker_type="nnom")
    dr = dockerRunner(root_dir, new_uuid, task_id, debug,pm , device_config, obj=knowledgepacks[0])
    dr.set_tensorflow_compile(target_arch,target_arch,"")

    shutil.copy(os.path.join(os.path.dirname(__file__),'../../library/model_zoo/data/mfcc23x49_w480_d320_dscnn_v02.h5'), f"/home/cknorow/test/{new_uuid}/model.h5")
    shutil.copy(os.path.join(os.path.dirname(__file__),'../../library/model_zoo/auxiliary_data/auxiliary_test.csv'), f"/home/cknorow/test/{new_uuid}/test.csv")
    
    print(dr.get_execution_params(build_type='source',application='AI Model Runner'))
    
    dr.build_code_bin('source', "AI Model Runner")
    
