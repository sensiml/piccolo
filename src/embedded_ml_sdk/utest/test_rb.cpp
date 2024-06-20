#include "gtest/gtest.h"
#include "rb.h"
#include "math.h"
#include <stdio.h>

#define BUFF_LEN 512

// App needs to allocate its buff[] to be pointed to by rb->buff;
static rb_data_t mybuff[BUFF_LEN] = {0}; // init to 0
static ringb rb;

static void init_rb()
{
    memset(mybuff, 0, sizeof(rb_data_t) * BUFF_LEN);
    rb_init(&rb, mybuff, BUFF_LEN);
}

/*
 * test head == tail at init state
 */
TEST(POW2_RB_INIT_TEST, invalid_test_test)
{
    init_rb();
    int i;
    for (i = 0; i < BUFF_LEN; i++)
    {
        ASSERT_EQ(0, rb_read(&rb, i));
    }

    int ret = rb_valid(&rb);

    // expect to be invalid
    // - after rb_setup()
    // - before rb_add()
    ASSERT_EQ(0, ret);
}

TEST(POW2_RB_ADD_PARTIAL_RING_TEST, add_but_yet_wrap_around_test)
{
    init_rb();

    int val = 123;
    int n_items = 100;
    int i;

    for (i = 0; i < n_items; i++)
    {
        rb_add(&rb, val);
    }

    /*
     * verify if the first half are all 1234
     */
    for (i = 0; i < n_items; i++)
    {
        ASSERT_EQ(val, rb_read(&rb, i));
    }
    ASSERT_EQ(1, rb_valid(&rb));

    /*
     * verify if the second half are 0 still
     */
    for (i = n_items; i < BUFF_LEN; i++)
    {
        ASSERT_EQ(0, rb_read(&rb, i));
    }

    /*
     * ring should be valid (tail != head)
     */
    ASSERT_EQ(1, rb_valid(&rb));
}

TEST(POW2_RB_ADD_WRAP_AROUND_TEST, PositiveTest)
{
    init_rb();

    int i;
    /*
     * write 0 to 1023 to ring buffer
     * - since ring size = 512, val in ring should be 512 to 1023
     */
    for (i = 0; i < 2 * BUFF_LEN; i++)
    {
        rb_add(&rb, i);
    }

    /*
     * verify if ring buffer is holding 512 to 1023 @ idx = 0 to 511
     */
    for (i = 0; i < BUFF_LEN; i++)
    {
        ASSERT_EQ(BUFF_LEN + i, rb_read(&rb, i));
    }

    /*
     * ring should be valid (tail != head)
     */
    ASSERT_EQ(1, rb_valid(&rb));
}

TEST(POW2_RB_WRITE_TEST, PositiveTest)
{
    init_rb();

    int val = 456;
    int n_items = 300;
    int i;

    for (i = 0; i < n_items; i++)
    {
        rb_write(&rb, i, val);
    }
    /*
     * verify if the first half are all 1234
     */
    for (i = 0; i < n_items; i++)
    {
        ASSERT_EQ(val, rb_read(&rb, i));
    }

    /*
     * ring should remain invalid since we have yet added any data
     */
    ASSERT_EQ(0, rb_valid(&rb));
}

TEST(POW2_NEXT, CorrectTest)
{

    int result = 0;
    int i;
    for (i = 2; i < 16; i++)
    {
        result = next_pow_2(pow(2, i) - 1);
        ASSERT_EQ(result, pow(2, i));
    }

    for (i = 2; i < 16; i++)
    {
        result = next_pow_2(pow(2, i));
        ASSERT_EQ(result, pow(2, i));
    }

    /*
     * ring should remain invalid since we have yet added any data
     */
}

TEST(POW2_RB_ADD_WRAP_AROUND_TEST, num_items)
{
    init_rb();

    int i;
    /*
     * write 0 to 1023 to ring buffer
     * - since ring size = 512, val in ring should be 512 to 1023
     */
    for (i = 0; i < BUFF_LEN / 2; i++)
    {
        rb_add(&rb, i);
        ASSERT_EQ(i + 1, rb_num_items(&rb, 0));
    }

    for (i = BUFF_LEN / 2; i <= BUFF_LEN * 4; i++)
    {
        /*
        * verify the item count is correct
        */
        ASSERT_EQ(BUFF_LEN / 2, rb_num_items(&rb, i - BUFF_LEN / 2));
        rb_add(&rb, i);
    }
}

TEST(RB_MATH_FUNCTIONS_TEST, multiply_axis_data)
{
    init_rb();

    int i;
    /*
     * write 0 to 1023 to ring buffer
     * - since ring size = 512, val in ring should be 512 to 1023
     */
    for (i = 0; i < BUFF_LEN / 2; i++)
    {
        rb_add(&rb, i);
        multiply_axis_data_float(&rb, i, .5);
        //printf("%d ,", rb_read(&rb, i));
        ASSERT_EQ(int16_t(i * .5), rb_read(&rb, i));
    }
}

TEST(RB_MATH_FUNCTIONS_TEST, multiply_axis_data_overflow)
{
    init_rb();

    int i;
    /*
     * write 0 to 1023 to ring buffer
     * - since ring size = 512, val in ring should be 512 to 1023
     */
    for (i = 0; i < BUFF_LEN / 2; i++)
    {
        rb_add(&rb, i + 1);
        multiply_axis_data_float(&rb, i, 40000);
        //printf("%d ,", rb_read(&rb, i));
        ASSERT_EQ(0x7FFF, rb_read(&rb, i));
    }
}

/*
int main(int argc, char *argv[]) {
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
*/
