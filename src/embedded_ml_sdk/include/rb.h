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
 * @file rb.h
 * @author Thawee Techathamnukool, Chris Knorowski
 * @data May 08, 2017
 * @brief File containing ring buffer implementation for NBI-JV Knowledge Pack.
 *
 * Since the knowledge pack needs to maintain an array of sensor samples with
 * sliding window access for its computation, ring buffer data structure is
 * needed.
 *
 * This ring buffer implementation requires the ring size to be power of 2 for
 * fast lookup using ring mask.
 *
 * List of APIs
 * rb_init(*rb, *buff, len) : init *rb to an array buff and setting its buff len
 * rb_add(*rb, val) : add new val to *rb (enqueue)
 * rb_read(*rb, idx) : get a val from *rb providing an index
 *
 * Old APIs to compat with old RB implementation
 * setup_rb() : same as rb_init()
 * readrb16() : same as rb_read() assuming data type is short
 *
 */

#ifndef _POW2_RB_H_
#define _POW2_RB_H_

#define RB_POW2

#include <stdbool.h>
#include <stdint.h>
#include "kb_typedefs.h"

#ifdef __cplusplus
extern "C"
{
#endif

  // Needed?
  // ##define INLINE INLINE static

  /**
   * kbdefs.h??
   */
  // typedef unsigned short uint16_t;

  /**
   * good name?  here?
   */
  typedef short rb_data_t;

/*
 * These Macros are defined to simplify the use of read and write to ring buffer
 */
#define MOD_READ_RINGBUF(ringb, index) ringb->buff[(index) & ringb->mask]
#define MOD_WRITE_RINGBUF(ringb, index, value) ringb->buff[(index) & ringb->mask] = value;

  /**
   * @brief ring buffer data structure.
   *
   * This ring buffer is an implementation over array data structure.
   * - init: head = tail = 0
   * - full: tail = head
   */
  typedef struct
  {
    /*@{*/
    uint16_t head;   /**< internal index to head of ring - oldest data */
    uint16_t tail;   /**< internal ring index to where the next data is */
    uint16_t mask;   /**< internal ring mask for fast lookup */
    rb_data_t *buff; /**< pointer to the array of data */
    int16_t stat;    /**< used to stare some info about this ring buffer */
    bool lock;       /**< this is a flag that is set when data should not be ovewritten
   Note: this is not enforced by the ring buffer but is used
   externally by the kp*/
                     /*@}*/
  } ringb, ring_buffer_t;

  /**
   * \brief Return the next power of 2
   *
   * @param[i] x - length to check
   *
   * @return nearest power of 2
   */
  int32_t next_pow_2(uint16_t x);

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

  void rb_init(ringb *rb, rb_data_t *buffer, uint16_t ring_size);

  void copy_rb_to_buff(ringb *rb, rb_data_t *buffer);

  void copy_segment_to_buff(ringb *rb, rb_data_t *buffer, int32_t index, int32_t length);

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
  void setup_rb(ringb *rb, rb_data_t *buffer, uint16_t ring_size);

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

  // Same as rb_init(), please use rb_init()
  // It is still here for code migration only and will be removed soon!
  void setup_rb_with_data(ringb *rb, rb_data_t *buffer, uint16_t ring_size, uint16_t data_size);

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
  rb_data_t rb_read(ringb *rb, uint16_t idx);
  //{
  //    return (rb->buff[idx & rb->mask]);
  //}

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
  rb_data_t rb_read_offset(ringb *rb, uint16_t offset);

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
  void rb_add(ringb *rb, rb_data_t data);

  /**
   * Reset the ring buffer effectivley clearing out the data
   *
   * @param[in] rb   Pointer to a ringb.
   *
   * @return None
   */
  void rb_reset(ringb *rb);
  //{
  //    rb->tail = 0;
  //    rb->head = 0;
  //}

  /**
   * Reset the ring buffer effectivley clearing out the data
   *
   * @param[in] rb   Pointer to a ringb.
   *
   * @return None
   */
  void rb_step_head(ringb *rb, int32_t delta);
  //{
  //  rb->head = (rb->head + delta) & rb->mask;
  //}
  //

  /**
   * Overwrite sample value to a specific index of the ring buffer
   *
   * @param[in] rb   Pointer to a ringb.
   * @param[in] data Value of the sample to be added into the ring buffer
   * @param[in] idx  Sample index to be read from ring buffer.
   *
   * @return None
   */
  void rb_write(ringb *rb, uint16_t idx, rb_data_t val);
  //{
  //    rb->buff[idx & rb->mask] = val;
  //}

  /**
   * get_axis_data() To be deplicated??
   *
   * get_axis_dta() is the same as rb_read().  Should we eliminate one?
   */
  rb_data_t get_axis_data(ringb *rb, int32_t idx);

  /**
   * readrb16() To be deplicated??
   *
   * readrb16() is the same as rb_read().  Should we eliminate one?
   */
  rb_data_t readrb16(ringb *rb, int32_t idx);

  /**
   * pushrb16() To be deplicated??
   *
   * pushrb16() is the same as rb_write() expect that it also return 'tail'
   */
  int32_t pushrb16(ringb *rb, rb_data_t val);

  /**
   *
   */
  int32_t rb_valid(ringb *rb);

  /*
   * Print API for debugging only
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

  /**
   * lock the ring buffer.
   */
  void rb_lock(ringb *rb);

  /**
   * unlock the ring buffer.
   */
  void rb_unlock(ringb *rb);

  bool rb_status(ringb *rb);

  /**
   * Write a new value to a location in the ring buffer.
   *
   * @param[in] rb the pointer to ring buffer structure
   * @param[in] idx the pointer to the pre masked index of the ring buffer
   * @param[in] data the value to insert into the ring buffer
   */
  void write_axis_data(ringb *rb, int32_t idx, rb_data_t data);

  /**
   * Multiply a data point in ring buffer by value.
   * recasts to rb_data_t after multiplcation
   *
   * @param[in] rb the pointer to ring buffer structure
   * @param[in] idx the pointer to the pre masked index of the ring buffer
   * @param[in] data value to multiple by
   */
  void multiply_axis_data(ringb *rb, int32_t idx, rb_data_t data);

  /**
   * Multiply a data point in ring buffer by float value.
   * recasts to rb_data_t after multiplcation
   *
   * @param[in] rb the pointer to ring buffer structure
   * @param[in] idx the pointer to the pre masked index of the ring buffer
   * @param[in] data value to multiple by
   */
  void multiply_axis_data_float(ringb *rb, int32_t idx, float data);

  /**
   * Divide a data point in ring buffer by value. will recast to rb_data_t
   *
   * @param[in] rb the pointer to ring buffer structure
   * @param[in] idx the pointer to the pre masked index of the ring buffer
   * @param[in] data value to divide by
   */
  void divide_axis_data(ringb *rb, int32_t idx, rb_data_t data);

  /**
   * Divide a data point in ring buffer by float value. After divide, value is reacast to rb_data_t
   *
   * @param[in] rb the pointer to ring buffer structure
   * @param[in] idx the pointer to the pre masked index of the ring buffer
   * @param[in] data value to divide by
   */
  void divide_axis_data_float(ringb *rb, int32_t idx, float data);

  /**
   * Add a value to a point in the ring buffer.
   * (note: does not check for int32_t overflow, should we recast?)
   *
   * @param[in] rb the pointer to ring buffer structure
   * @param[in] idx the pointer to the pre masked index of the ring buffer
   * @param[in] data value to add
   */
  void add_axis_data(ringb *rb, int32_t idx, rb_data_t data);

  /**
   * Get the number of items in the ring buffer after a specific index.
   *
   * @param[in] rb the pointer to ring buffer structure
   * @param[in] idx the pointer to the pre masked index of the ring buffer
   */
  int32_t rb_num_items(ringb *rb, int32_t idx);

  /**
   * Get the number of items in the ring buffer.
   *
   * @param[in] rb the pointer to ring buffer structure
   */
  int32_t rb_items(ringb *rb);
//{
//    return (rb->tail - rb->head +rb->mask) & rb->mask ;
//}

/**
 * Initialize a 16 bits ringb data
 * @param[in] prb Pointer to a ringb.
 * @param[in] p the pointer of a buffer.
 * @param[in] rblen the length of data in the ring buffer
 * @param[in] rbcnt the number of ring buffer
 * @return always 1
 */
// int32_t initrb_array(ringb *prb, short *p, int32_t rblen, int32_t rbcnt);
/*
{
int32_t i = 0;
if (p == 0 || prb == 0 || rbcnt <= 0 || rblen <= 0) return 0;
for (i = 0; i < rbcnt; i++)
initrb(prb + i, p + rblen*i, rblen, 0, 0);
return 1;
}
*/
#ifdef __cplusplus
}
#endif

#endif /* _POW2_RB_H_ */