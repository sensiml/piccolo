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




/*
 * Author(s) : Giuseppe Raffa, Noura Farra
 * Group : IXR/Intel Labs
 * modified to linux kernel coding style by Alek Du (PSI, MCG)
 * code cleanup and maintained by Han Ke (PSI, MCG)
 */

#ifndef MOV_DETECT_H
#define MOV_DETECT_H


#ifdef __cplusplus
#if __cplusplus
extern "C"{
#endif
#endif /* __cplusplus */ 


#include "gesturespotting.h"

#define MAX_BACKTRACK_QUEUE_SIZE 50
    /*
    this block needs to buffer data ax ay az gx gy gz
    this part can and *should* be optimized if data are available elsewhere in the
    system and just keep a pointer to the first sample to keep track of the
    initial sample of the movement.
    this optimization can only be done once the module has been integrated in the
    final architecture
    For now we assume a static memory of 3 seconds: 3sec*100hz
    In #samples. each sample is 6 2bytes items: ax ay az gx gy gz
    */
#define MAX_CURRENT_DATA_SIZE_SAMPLES 300

    enum { USE_FORWARD = 0, USE_BACKWARD = 1 };

    /* public functions */
    u8 mov_detect_init(s16 one_g,
    struct mov_detect_struct_init *md,
    struct mov_detect_struct_init *md_h,
        u8 use_forward_or_backward,
        u8 _true_use_accel_false_use_gyro,
        u8 _true_use_avg_false_use_std,
        void *sample_buf,
        int sample_buf_size);

    /* WE ASSUME THE VECTOR IS 6 s16 AND THE ORDER IS AX,AY,AZ,GX,GY,GZ */
    void mov_detect_calculate(s16* orig_raw_data, struct gesture_struct *g);
    void mov_detect_startrec(void);
    void mov_detect_stoprec(int g_ok);



#ifdef __cplusplus
#if __cplusplus
}
#endif
#endif /* __cplusplus */



#endif
