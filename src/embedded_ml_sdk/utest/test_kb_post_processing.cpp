#include "gtest/gtest.h"
#include "kb_post_processing.h"

#define SIZE 3
#define FEATURE_LENGTH 5

static FLOAT feature_0[5] = {1, 2, 3, 4, 5};
static FLOAT feature_1[5] = {1, 8, 2, 3, 4};
static FLOAT feature_2[5] = {1, -4, 1, 0, 6};
static FLOAT feature12_sum[5] = {2, 4, 3, 3, 10};
static FLOAT feature12_avg[5] = {1, 2, 1.5, 1.5, 5};

static feature_set_t feature_set[0];
class PostProcessingTest : public testing::Test
{
protected:
    virtual void SetUp()
    {
        uint16_t buffer_size = get_buffer_size(SIZE, FEATURE_LENGTH);
        FLOAT *buffer = (FLOAT *)malloc(buffer_size * sizeof(FLOAT));
        setup_feature_set(feature_set, SIZE, FEATURE_LENGTH, buffer);
    }
};

TEST_F(PostProcessingTest, kb_feature_set_create_test)
{
    uint16_t index;

    ASSERT_EQ(feature_set->size, SIZE);
    ASSERT_EQ(feature_set->num_elements, 0);
    ASSERT_EQ(0, feature_set->index);

    index = head_index_feature_set(feature_set);
    ASSERT_EQ(0, index);
}

TEST_F(PostProcessingTest, kb_push_one_feature_test)
{

    push_feature(feature_set, feature_1);
    ASSERT_EQ(feature_set->size, SIZE);
    ASSERT_EQ(feature_set->num_elements, 1);
    ASSERT_EQ(1, feature_set->index);

    for (int i = 0; i < FEATURE_LENGTH; i++)
    {
        ASSERT_EQ(feature_set->sum[i], feature_1[i]);
        ASSERT_EQ(feature_set->average[i], feature_1[i]);
    }
}

TEST_F(PostProcessingTest, kb_push_two_features_test)
{
    FLOAT head_feature[5];
    uint16_t index;

    push_feature(feature_set, feature_1);
    push_feature(feature_set, feature_2);
    ASSERT_EQ(feature_set->size, SIZE);
    ASSERT_EQ(feature_set->num_elements, 2);
    ASSERT_EQ(2, feature_set->index);

    for (int i = 0; i < FEATURE_LENGTH; i++)
    {
        ASSERT_EQ(feature_set->sum[i], feature12_sum[i]);
        ASSERT_EQ(feature_set->average[i], feature12_avg[i]);
    }

    index = head_index_feature_set(feature_set);
    ASSERT_EQ(0, index);

    get_head_feature_set(feature_set, head_feature);
    for (int i = 0; i < FEATURE_LENGTH; i++)
    {
        ASSERT_EQ(head_feature[i], feature_1[i]);
    }
}

TEST_F(PostProcessingTest, kb_head_features_test)
{
    FLOAT head_feature[5];
    uint16_t index;

    push_feature(feature_set, feature_0);
    push_feature(feature_set, feature_1);
    push_feature(feature_set, feature_0);
    push_feature(feature_set, feature_2);

    index = head_index_feature_set(feature_set);
    ASSERT_EQ(1, index);

    get_head_feature_set(feature_set, head_feature);
    for (int i = 0; i < FEATURE_LENGTH; i++)
    {
        ASSERT_EQ(head_feature[i], feature_1[i]);
    }
}

TEST_F(PostProcessingTest, kb_tail_features_test)
{
    FLOAT tail_feature[5];
    uint16_t index;

    push_feature(feature_set, feature_0);
    push_feature(feature_set, feature_1);
    push_feature(feature_set, feature_0);
    push_feature(feature_set, feature_2);

    index = tail_index_feature_set(feature_set);
    ASSERT_EQ(0, index);

    get_tail_feature_set(feature_set, tail_feature);
    for (int i = 0; i < FEATURE_LENGTH; i++)
    {
        ASSERT_EQ(tail_feature[i], feature_2[i]);
    }
}

TEST_F(PostProcessingTest, kb_feature_at_index_test)
{
    FLOAT feature[5];

    push_feature(feature_set, feature_0);
    push_feature(feature_set, feature_1);
    push_feature(feature_set, feature_0);
    push_feature(feature_set, feature_2);

    get_feature_at_index(feature_set, 0, feature);
    for (int i = 0; i < FEATURE_LENGTH; i++)
    {
        ASSERT_EQ(feature[i], feature_1[i]);
    }

    get_feature_at_index(feature_set, 1, feature);
    for (int i = 0; i < FEATURE_LENGTH; i++)
    {
        ASSERT_EQ(feature[i], feature_0[i]);
    }

    get_feature_at_index(feature_set, 2, feature);
    for (int i = 0; i < FEATURE_LENGTH; i++)
    {
        ASSERT_EQ(feature[i], feature_2[i]);
    }
}

TEST_F(PostProcessingTest, kb_base_index_feature_set)
{
    uint_fast16_t base_index;

    push_feature(feature_set, feature_0);
    push_feature(feature_set, feature_1);
    push_feature(feature_set, feature_0);
    push_feature(feature_set, feature_2);

    base_index = base_index_feature_set(feature_set);
    ASSERT_EQ(base_index, 1);

    push_feature(feature_set, feature_2);
    base_index = base_index_feature_set(feature_set);
    ASSERT_EQ(base_index, 2);
}

TEST_F(PostProcessingTest, kb_pop_first_feature)
{
    uint_fast16_t index;
    FLOAT head_feature[5];
    FLOAT tail_feature[5];

    push_feature(feature_set, feature_0);
    push_feature(feature_set, feature_1);
    push_feature(feature_set, feature_2);

    ASSERT_EQ(3, feature_set->num_elements);

    pop_first_feature(feature_set);

    ASSERT_EQ(2, feature_set->num_elements);
    ASSERT_EQ(0, feature_set->index);

    index = head_index_feature_set(feature_set);
    ASSERT_EQ(1, index);

    get_head_feature_set(feature_set, head_feature);
    get_tail_feature_set(feature_set, tail_feature);
    for (int i = 0; i < FEATURE_LENGTH; i++)
    {
        ASSERT_EQ(head_feature[i], feature_1[i]);
        ASSERT_EQ(tail_feature[i], feature_2[i]);
        ASSERT_EQ(feature_set->sum[i], feature12_sum[i]);
        ASSERT_EQ(feature_set->average[i], feature12_avg[i]);
    }

    ASSERT_EQ(2, feature_set->num_elements);
}

TEST_F(PostProcessingTest, kb_pop_last_feature)
{
    uint_fast16_t index;
    FLOAT tail_feature[5];

    push_feature(feature_set, feature_0);
    push_feature(feature_set, feature_1);
    push_feature(feature_set, feature_2);
    push_feature(feature_set, feature_0);

    pop_last_feature(feature_set);

    index = tail_index_feature_set(feature_set);
    ASSERT_EQ(2, index);

    get_tail_feature_set(feature_set, tail_feature);
    for (int i = 0; i < FEATURE_LENGTH; i++)
    {
        ASSERT_EQ(tail_feature[i], feature_2[i]);
        ASSERT_EQ(feature_set->sum[i], feature12_sum[i]);
        ASSERT_EQ(feature_set->average[i], feature12_avg[i]);
    }

    ASSERT_EQ(2, feature_set->num_elements);
}
