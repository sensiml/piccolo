.. meta::
   :title: Knowledge Packs / Model Firmware - Storing and Loading a PME Model
   :description: How to store and load a PME model with a Knowledge Pack

===============================
Storing and Loading a PME model
===============================

These are SensiML APIs that are used to loading/saving of models at edge devices. Knowledge Packs store the initial models in code space. If you are updating models, you will need to store and read from your devices non-volatile memory. These APIs describe a method for enabling this behavior. This enables Knowledge Packs with PME classifiers to read_model_pattern_from_flash federated learning, where one device learns new patterns and uploads it to a central repository, which then pushes the new patterns down to other devices.

Knowledge Pack API
------------------

.. code-block:: C

    typedef struct{
        uint16_t influence; //influence of a pattern
        uint16_t category; //category of pattern
        uint8_t * vector; // vector containing the features of a pattern
        } pattern_t;

    typedef struct{
        uint16_t number_patterns; //influence of a pattern
        uint16_t pattern_length; //category of pattern
        } model_header_t;


    /**
    * Get the number of patterns currently stored by a model
    * as well as the length
    *
    *  (Note: All patterns in a model have the same length)
    *
    * @param[in] model_index Model index to use.
    * @param[in] model_header model_header_t object to store model header in.
    */
    int get_model_header(int model_index, model_header_t * model_header);


    /**
    * Fill a pattern struct with the information about a pattern of a model
    *
    * @param[in] model_index Model index to use.
    * @param[in] pattern_id index of pattern to fill patern struct with.
    * @param[in] pattern pattern_t struct modify with information of pattern_id
    */
    void get_model_pattern(int model_index, int pattern_id, pattern_t * pattern);

    /**
    * Set the number of patterns stored in SRAM to 0 for the model index
    *
    * @param[in] model_index Model index to use.
    */
    void flush_model(int model_index);


Application Code
----------------

You are expected to write the following APIs for your device. We have provided some example code that can be modified to support your specific need.


.. code-block:: C

    void write_header_to_flash(model_header_t * model_header);
    void write_pattern_to_flash(pattern_t * pattern);
    void read_model_pattern_from_flash(int pattern_index, pattern_t * pattern);
    void read_model_header_from_flash(model_header_t * model_header);


Recommended Binary Structure
----------------------------

The first line is the information contained in the model_header_t object, then each subsequent line is the information contained in the pattern_t object after filling it with a pattern index.

.. code-block:: C

    uint16_t number_of_patterns, uint16_t pattern_length;
    uint16_t influence, uint16_t category, uint8_t feature_1, uint8_t feature_2, uint8_t feature_3; //etc, etc.
    uint16_t influence, uint16_t category, uint8_t feature_1, uint8_t feature_2, uint8_t feature_3; //etc, etc.
    uint16_t influence, uint16_t category, uint8_t feature_1, uint8_t feature_2, uint8_t feature_3; //etc, etc.


Writing a model to flash
------------------------

.. code-block:: C

    void write_model_to_flash(int model_index)
    {
        pattern_t pattern;
        model_header_t model_header;

        get_model_header(model_index, &model_header);

        write_header_to_flash(&model_header); //END USER DEFINED

        for (int pattern_id=0; pattern_id < model_header.number_patterns; pattern_id++)
        {
            get_model_pattern(model_index, pattern_id, &pattern);
            write_pattern_to_flash(&pattern); //END USER DEFINED
        }
    }


Loading a model from flash
--------------------------

.. code-block:: C

    void read_model_from_flash(int model_index)
    {
        model_header_t model_header;
        pattern_t pattern;

        flush_model(model_index); // SET THE NUMBER OF PATTERNS STORED IN SRAM TO 0

        read_model_header_from_flash(&model_header);

        for (int pattern_id=0; pattern_id<model_header.number_patterns; pattern_id++)
        {
            read_model_pattern_from_flash(pattern_id, &pattern); //END USER DEFINED
            add_custom_patern_to_model(model_index, pattern.vector, pattern.category, pattern.influence);
        }

    }

