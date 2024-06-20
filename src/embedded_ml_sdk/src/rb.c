/*
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
*/




/**
 *
 * Since the knowledge pack needs to maintain an array of sensor samples with
 * sliding window access for its computation, ring buffer data structure is
 * needed.
 *
 * This ring buffer implementation requires the ring size to be power of 2 for
 * fast lookup using ring mask.
 *
 */

#include "rb.h"

#if SML_DEBUG
#include "assert.h"

/**
 * \brief Check if a number of power 2
 *
 * @param[i] x - number to be checked
 *
 * @return non-zero if yes, otherwise 0
 */
static int32_t is_pow2(uint16_t x)
{
    return ((x != 0) && ((x & (~x + 1)) == x));
}

#endif

/**
 * \brief Return the next power of 2
 *
 * @param[i] x - length to check
 *
 * @return nearest power of 2
 */
int32_t next_pow_2(uint16_t x)
{
    x--;
    x |= x >> 1;
    x |= x >> 2;
    x |= x >> 4;
    x |= x >> 8;
    x |= x >> 16;
    x++;

    return x;
}

/**
 * \brief Initialize the ring buffer.
 *
 * Initialize the ring buffer before start using.
 * - Ring will be empty
 * - Ring will be pointed to array
 * - Ring size must be provided and must be power of 2
 * - Ring mask is used internally under ring buffer APIs for fast lookup
 *
 * @param[in] rb the pointer to ring buffer structure
 * @param[in] ring_size size of the ring buffer
 * @param[in] buffer the pointer the array
 *
 * @return None
 */

void rb_init(ringb *rb, rb_data_t *buffer, uint16_t ring_size)
{
#if SML_DEBUG
    assert(is_pow2(ring_size) != 0);
    assert(rb);
    assert(buffer);
#endif

    rb->head = 0;
    rb->tail = 0;
    rb->mask = ring_size - 1; // ring_size must be power of 2
    rb->buff = buffer;
    rb->stat = 0;
}

/**
 * Setup the Ring Buffer.
 *
 * Setup the ring buffer with the user provided
 * buffer to be used as well as its size.
 *
 * @param[in] rb Pointer to a ringb.
 * @param[in] buffer Array for the ring buffer.
 * @param[in] size Size of the rng buffer.
 *
 * @return None
 */

// Same as rb_init(), please use rb_init()
// It is still here for code migration only and will be removed soon!
void setup_rb(ringb *rb, rb_data_t *buffer, uint16_t ring_size)
{
#if SML_DEBUG
    assert(is_pow2(ring_size) == 0);
    assert(rb);
    assert(buffer);
#endif
    rb->head = 0;
    rb->tail = 0;             // size = next to be written index = tail
    rb->mask = ring_size - 1; // ring_size must be power of 2
    rb->buff = buffer;
}

/**
 * Setup the Ring Buffer with a filled/partiall filled segment.
 *
 * Setup the ring buffer with the user provided
 * buffer to be used as well as its size.
 *
 * @param[in] rb Pointer to a ringb.
 * @param[in] buffer Array for the ring buffer.
 * @param[in] size Size of the rng buffer.
 * @param[in] size sensor data in the ring buffer.
 *
 * @return None
 */

void copy_rb_to_buff(ringb *rb, rb_data_t *buffer)
{
    int32_t nitems = rb_items(rb);

    for (int i = 0; i <= nitems; i++)
    {
        buffer[i] = rb_read(rb, rb->head + i);
    }
}

void copy_segment_to_buff(ringb *rb, rb_data_t *buffer, int32_t index, int32_t length)
{

    for (int i = 0; i <= length; i++)
    {
        buffer[i] = rb_read(rb, index + i);
    }
}

// Same as rb_init(), please use rb_init()
// It is still here for code migration only and will be removed soon!
void setup_rb_with_data(ringb *rb, rb_data_t *buffer, uint16_t ring_size, uint16_t data_size)
{
#if SML_DEBUG
    assert(is_pow2(ring_size) == 0);
    assert(rb);
    assert(buffer);
#endif
    rb->head = 0;
    rb->tail = 0;             // size = next to be written index = tail
    rb->mask = ring_size - 1; // ring_size must be power of 2
    rb->buff = buffer;

    rb->tail = (rb->tail + data_size) & rb->mask;

    if (rb->tail == rb->head)
    {
        rb->head = (rb->head + 1) & rb->mask;
    }
}

/**
 * Read sample value from ring buffer using index to buffer
 *
 * This read API needs a pointer to the ring buffer and sample index.
 *
 * @param[in] rb   Pointer to a ringb.
 * @param[in] idx  Sample index to be read from ring buffer.
 *                 - idx value : 0 - mask, then wrap around
 *                 - caller can pass any idx value, this function wil
 *                   handle the wrap around index before accessing *rb
 *
 * @return Value of sample at provided index.
 */
rb_data_t rb_read(ringb *rb, uint16_t idx)
{
#if SML_DEBUG
    assert(rb);
#endif
    return (rb->buff[idx & rb->mask]);
}

/*
 * Read sample value from ring buffer using offset from head (oldest sample)
 *
 * This read API needs a pointer to the ring buffer and offset.
 *
 * @param[in] rb   Pointer to a ringb.
 * @param[in] offset   Offset from head to read from ring buffer.
 *
 * @return Value of sample at provided offset.
 */
rb_data_t rb_read_offset(ringb *rb, uint16_t offset)
{
#if SML_DEBUG
    assert(rb);
#endif
    return (rb->buff[(rb->head + offset) & rb->mask]);
}

/**
 * Add one new sample value to the tail of ring buffer
 *
 * Since 'tail' is pointing where the new value to be added, it simply write
 * that value into that array[tail].
 * Next, it takes care of the index wraparound, by +1 & mask.
 * Then, it takes care of the 'head' if 'head' needs to be advanced.
 *
 * @param[in] rb   Pointer to a ringb.
 * @param[in] data Value of the sample to be added into the ring buffer
 *
 * @return None
 */
void rb_add(ringb *rb, rb_data_t data)
{
#if SML_DEBUG
    assert(rb);
#endif
    rb->buff[rb->tail] = data;
    rb->tail = (rb->tail + 1) & rb->mask;

    if (rb->tail == rb->head)
    {
        rb->head = (rb->head + 1) & rb->mask;
    }
}

/**
 * Overwrite sample value to a specific index of the ring buffer
 *
 * @param[in] rb   Pointer to a ringb.
 * @param[in] data Value of the sample to be added into the ring buffer
 * @param[in] idx  Sample index to be read from ring buffer.
 *
 * @return None
 */
void rb_write(ringb *rb, uint16_t idx, rb_data_t val)
{
#if SML_DEBUG
    assert(rb);
#endif
    rb->buff[idx & rb->mask] = val;
}

/**
 * get_axis_data() To be deplicated??
 *
 * get_axis_dta() is the same as rb_read().  Should we eliminate one?
 */
rb_data_t get_axis_data(ringb *rb, int32_t idx)
{
#if SML_DEBUG
    assert(rb);
#endif
    return (rb->buff[idx & rb->mask]);
}

/**
 * Add one new sample value to the tail of ring buffer
 *
 * Since 'tail' is pointing where the new value to be added, it simply write
 * that value into that array[tail].
 * Next, it takes care of the index wraparound, by +1 & mask.
 * Then, it takes care of the 'head' if 'head' needs to be advanced.
 *
 * @param[in] rb   Pointer to a ringb.
 * @param[in] data Value of the sample to be added into the ring buffer
 *
 * @return None
 */

void rb_reset(ringb *rb)
{
    rb->tail = 0;
    rb->head = 0;
    rb->stat = 0;
    rb->lock = false;
}

/**
 * Reset the ring buffer effectivley clearing out the data
 *
 * @param[in] rb   Pointer to a ringb.
 * @param[in] delta step side
 * @return None
 */
void rb_step_head(ringb *rb, int32_t delta)
{
    rb->head = (rb->head + delta) & rb->mask;
}

/**
 *
 */
int32_t rb_valid(ringb *rb)
{
#if SML_DEBUG
    assert(rb);
#endif
    return (rb->tail != rb->head);
}

/**
 * Set ring buffer lock to True
 */
void rb_lock(ringb *rb)
{
    rb->lock = true;
}

/**
 * Set ring buffer lock to False.
 */
void rb_unlock(ringb *rb)
{
    rb->lock = false;
}

/**
 * Get the status of the ring buffer.
 */
bool rb_status(ringb *rb)
{
    return rb->lock;
}

/**
 * Write a new value to a location in the ring buffer.
 *
 * @param[in] rb the pointer to ring buffer structure
 * @param[in] idx the pointer to the pre masked index of the ring buffer
 * @param[in] data the value to insert into the ring buffer
 */
void write_axis_data(ringb *rb, int32_t idx, rb_data_t data)
{
    rb->buff[idx & rb->mask] = data;
}

/**
 * Multiply a data point in ring buffer by value.
 * recasts to rb_data_t after multiplcation
 *
 * @param[in] rb the pointer to ring buffer structure
 * @param[in] idx the pointer to the pre masked index of the ring buffer
 * @param[in] data value to multiple by
 */
void multiply_axis_data(ringb *rb, int32_t idx, rb_data_t data)
{
    int32_t value = rb->buff[idx & rb->mask] * data;

    if (value > 0x7FFF)
    {
        value = 0x7FFF;
    }
    else if (value < -32768)
    {
        value = -32768;
    }

    rb->buff[idx & rb->mask] = (rb_data_t)value;
}

/**
 * Divide a data point in ring buffer by value. will recast to rb_data_t
 * (note: does not check for a zero divide value)
 *
 * @param[in] rb the pointer to ring buffer structure
 * @param[in] idx the pointer to the pre masked index of the ring buffer
 * @param[in] data value to divide by
 */
void divide_axis_data(ringb *rb, int32_t idx, rb_data_t data)
{

    if (data == 0)
    {
        rb->buff[idx & rb->mask] = 0x7FFF;
        return;
    }

    rb->buff[idx & rb->mask] /= data;
}

/**
 * Divide a data point in ring buffer by value. will recast to rb_data_t
 * (note: does not check for a zero divide value)
 *
 * @param[in] rb the pointer to ring buffer structure
 * @param[in] idx the pointer to the pre masked index of the ring buffer
 * @param[in] data value to divide by
 */
void divide_axis_data_float(ringb *rb, int32_t idx, float data)
{
    float tmp = 0;

    if (data == 0)
    {
        rb->buff[idx & rb->mask] = 0x7FFF;
        return;
    }

    tmp = (float)rb->buff[idx & rb->mask];

    tmp /= data;

    rb->buff[idx & rb->mask] = (rb_data_t)data;
}

/**
 * Divide a data point in ring buffer by value. will recast to rb_data_t
 * (note: does not check for a zero divide value)
 *
 * @param[in] rb the pointer to ring buffer structure
 * @param[in] idx the pointer to the pre masked index of the ring buffer
 * @param[in] data value to divide by
 */
void multiply_axis_data_float(ringb *rb, int32_t idx, float data)
{
    float value = 0;

    if (data == 0)
    {
        rb->buff[idx & rb->mask] = 0;
        return;
    }

    value = (float)rb->buff[idx & rb->mask];

    value *= data;

    if (value > 0x7FFF)
    {
        value = 0x7FFF;
    }
    else if (value < -32768)
    {
        value = -32768;
    }

    rb->buff[idx & rb->mask] = (rb_data_t)value;
}

/**
 * Add a value to a point in the ring buffer.
 * (note: does not check for int32_t overflow, should we recast?)
 *
 * @param[in] rb the pointer to ring buffer structure
 * @param[in] idx the pointer to the pre masked index of the ring buffer
 * @param[in] data value to add
 */
void add_axis_data(ringb *rb, int32_t idx, rb_data_t data)
{
    int32_t value = rb->buff[idx & rb->mask] + data;

    if (value > 0x7FFF)
    {
        value = 0x7FFF;
    }
    else if (value < -32768)
    {
        value = -32768;
    }

    rb->buff[idx & rb->mask] = (rb_data_t)value;
}

/**
 * Get the number of items in the ring buffer after a specific index.
 *
 * @param[in] rb the pointer to ring buffer structure
 * @param[in] idx the pointer to the pre masked index of the ring buffer
 *
 * NOTE: this will return rb_size when the tail and idx are the same value
 */
int32_t rb_num_items(ringb *rb, int32_t idx)
{
    return ((rb->tail - idx + rb->mask) & rb->mask) + 1;
}

/**
 * Get the number of items in the ring buffer.
 *
 * @param[in] rb the pointer to ring buffer structure
 */
int32_t rb_items(ringb *rb)
{
    return (rb->tail - rb->head + rb->mask) & rb->mask;
}

/*
 * Print API for SML_DEBUGging only
 * - print all data starting with [0]; not head
 */
/*
void rb_dump(ringb *rb) {
    int32_t i;
    int32_t len = rb->mask + 1;
//    printf("DUMP: head=%d tail=%d len=%d mask=0x%x [ ",
    pr_info(LOG_MODULE_MAIN, "DUMP: head=%d tail=%d len=%d mask=0x%x [ ",
        rb->head, rb->tail, len, rb->mask);

    for (i=0; i<len; i++) {
//        printf("%d ", rb->buff[i]);
        pr_info(LOG_MODULE_MAIN,"%d ", rb->buff[i]);
    }
//    printf("]\n");
    pr_info(LOG_MODULE_MAIN,"]\n");
}
*/

/*
int32_t initrb_array(ringb *prb, short *p, int32_t rblen, int32_t rbcnt)
{
    //rb_init(prb, p, rblen);
    int32_t i = 0;
    if (p == 0 || prb == 0 || rbcnt <= 0 || rblen <= 0) return 0;
    for (i = 0; i < rbcnt; i++)
        initrb(prb + i, p + rblen*i, rblen, 0, 0);
    return 1;
}
*/
