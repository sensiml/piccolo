.. meta::
   :title: API Methods - Knowledge Packs
   :description: How to use the Knowledge Pack API Method

Knowledge Packs
===============

The model that gets generated for your edge device is called a Knowledge Pack. A Knowledge Pack contains the device firmware code for detecting events in your application and will be flashed to your device. The Knowledge Pack contains all the information about how the model was trained, the metrics for the trained model, as well as the full trained pipeline model.


Download Knowledge Pack
-----------------------

To download a Knowledge Pack, you will need to create a configuration for the download.

The first part of the configuration is the kb_description, which describes the models that will be part of the Knowledge Pack. The format is as follows:

.. code-block:: python

   kb_description = {
      "MODEL_1": {
         "source": "<CAPTURE CONFIG UUID>",
         "uuid": "<Model UUID>"
      },
   }

Where model name can be whatever you choose. Source is the capture configuration that the model should use (this is used to set up the correct sensors and sample rate). uuid is the model UUID to use.

To get the UUID of the capture configuration and Knowledge Pack for a particular project use the following:

.. code-block:: python

   client.project.list_knowledgepacks()

   client.list_capture_configurations()


Next we will create the config for the download. To see a list of available target platforms along with their application and output_options use:

.. code-block:: python

   client.platforms_v2()

You can generate the template configuration by using the following

.. code-block:: python

   config = client.platforms_v2.get_platform_by_name('x86 GCC Generic').get_config()

replace the "x86 GCC Generic" platform name with the platform you would like to download.

.. code-block:: python

   print(config)

   {'target_platform': '26eef4c2-6317-4094-8013-08503dcd4bc5',
   'test_data': '',
   'debug': False,
   'output_options': ['serial'],
   'application': 'SensiML AI Model Runner',
   'target_processor': '822581d2-8845-4692-bcac-4446d341d4a0',
   'target_compiler': '62aabe7e-4f5d-4167-a786-072e468dc158',
   'float_options': '',
   'selected_platform_version': ''}

   config["kb_description"] = kb_description

And finally, we can now download the model as a library source (if supported by your subscription) or binary (if supported by your platform).

.. code-block:: python

   kp = client.get_knowledgepack("<MODEL UUID>")

   kp.download_library_v2(config=config)
   # kp.download_binary_v2(config=config)
   # kp.download_source_v2(config=config)


Multi Model Knowledge Pack
---------------------------

If you want to download multiple Knowledge Packs at once you will need to use the programmatic interface. Models can either be Parent or Children Models. Parent models require a **source**. Children models require a **segmenter_from** and **parent** flag. Optional flags are **results** which allows a **Child** model to be called depending on the output of a Parent model.

The model graphs are defined in the kb_description. The format for multiple parent models is as follows:

.. code-block:: json

   {
      "MODEL_1": {
         "source": "<CAPTURE CONFIG UUID>",
         "uuid": "<Model UUID>"
      },
      "MODEL_2": {
         "source": "<CAPTURE CONFIG UUID>",
         "uuid": "<Model UUID>"
      },
      "MODEL_3": {
         "source": "<CAPTURE CONFIG UUID>",
         "uuid": "<Model UUID>"
      }
   }


The format for multiple parent models and with multiple child models is as follows:

.. code-block:: json

   {
      "PARENT_1": {
         "source": "<CAPTURE CONFIG UUID>",
         "uuid": "<Model UUID>",
         "results": {
               "1": "CHILD_1",
               "2": "CHILD_2"
         }
      },
      "PARENT_2": {
         "source": "<CAPTURE CONFIG UUID>",
         "uuid": "<Model UUID>",
      },
      "CHILD_1": {
         "uuid": "<Model UUID>",
         "parent": "PARENT_1",
         "results": {
               "1": "Child 4",
         },
         "segmenter_from": "parent"
      },
      "CHILD_2": {
         "uuid": "<Model UUID>",
         "parent": "PARENT_1",
         "segmenter_from": "parent"
      },
      "CHILD_3": {
         "uuid": "<Model UUID>",
         "parent": "PARENT_1",
         "segmenter_from": "parent"
      },
      "CHILD_4": {
         "uuid": "<Model UUID>",
         "parent": "PARENT_1",
         "segmenter_from": "parent"
      }
   }


Import and Export Model
------------------------

In some instances you may want to import or export the model you have created. To support this you can you use the create and export API. 

To export a model, use the export() API shown below.


.. code-block:: python

   import json

   kp = client.get_knowledgepack("<MODEL UUID>")

   exported_model = kp.export()

   json.dump(exported_model, open('exported-model.json','w'))


You can then import that model and upload it to the server under a new name.

.. code-block:: python

   from sensiml.datamanager.knowledgepack import KnowledgePack


   kp = KnowledgePack(client._connection, client.project.uuid)

   kp.initialize_from_dict(json.load(open("exported-model.json",'r')))

   kp._name = "Imported Model"

   kp.create()



.. automodule:: sensiml.datamanager.knowledgepack
    :members: KnowledgePack

   
