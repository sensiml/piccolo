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

#include "gesturespotting.h"
#include "templatematching.h"
#include "movementdetection.h"

static u8 use_template_matching_filtering = 1;
// #ifdef CONFIG_BOARD_MOOREFIELD   // Moorefield parameters
#if 0
static struct mov_detect_struct_init m_default = {250, -1, 100, -1, 10, 17, 2};
static struct mov_detect_struct_init m_default_high = {250, -1, 100, -1, 10, 17, 2};
static struct mov_detect_struct_init m_btrack = {-1, -1, 100, -1, 3, 3, -1};
static struct mov_detect_struct_init m_btrack_high = {-1, -1, 100, -1, 3, 3, -1};
#endif

// Zhiqiang Liang's parameters:
static struct mov_detect_struct_init m_default = {120, -1, 100, -1, 10, 50, 2};
static struct mov_detect_struct_init m_default_high = {120, -1, 100, -1, 10, 50, 2};
static struct mov_detect_struct_init m_btrack = {-1, -1, 100, -1, 3, 3, -1};
static struct mov_detect_struct_init m_btrack_high = {-1, -1, 100, -1, 3, 3, -1};

/*#else // gs is disabled in Merrifield
static struct mov_detect_struct_init m_default = {300, -1, 200, -1, 10, 8, 2};
static struct mov_detect_struct_init m_default_high = {350, -1, 300, -1, 10, 13, 2};
static struct mov_detect_struct_init m_btrack = {-1, -1, 100, -1, 3, 3, -1};
static struct mov_detect_struct_init m_btrack_high = {-1, -1, 200, -1, 3, 3, -1};
#endif*/
static u8 gs_init_flag = 0;

u8 gesture_spot_init(s16 one_g, struct template_entry t[], u8 num_dim_template, int use_default_template_entry, struct mov_detect_struct_init *m_f,
                     struct mov_detect_struct_init *m_b, int use_default_mov_detect, int _use_template_matching_filtering, void *sample_buf, int sample_buf_size)
{
    u8 flag_md1, flag_md2, flag_tm;

    if (unlikely(t == NULL || m_f == NULL || m_b == NULL || sample_buf == NULL))
    {
        gs_init_flag = 0;
        return gs_init_flag;
    }

    use_template_matching_filtering = _use_template_matching_filtering;

    if (unlikely(use_default_mov_detect))
    {
        flag_md1 = mov_detect_init(one_g, &m_default, &m_default_high, USE_FORWARD, 1, 1, sample_buf, sample_buf_size);
        flag_md2 = mov_detect_init(one_g, &m_btrack, &m_btrack_high, USE_BACKWARD, 1, 1, sample_buf, sample_buf_size);
    }
    else
    {
        flag_md1 = mov_detect_init(one_g, m_f, m_f, USE_FORWARD, 1, 1, sample_buf, sample_buf_size);
        flag_md2 = mov_detect_init(one_g, m_b, m_b, USE_BACKWARD, 1, 1, sample_buf, sample_buf_size);
    }

    flag_tm = temp_match_init(one_g, t, TEMPLATE_MATHING_NUM_DIM);

    if (likely(flag_md1 == 1 && flag_md2 == 1 && flag_tm == 1))
        gs_init_flag = 1;
    else
        gs_init_flag = 0;
    return gs_init_flag;
}

/*
 * Callback on each new sample:
 * len_bytes MUST be 12: accel xyz and gyro xyz.
 * in case gyro is disabled, gyro xyz will be 0,0,0
 */
int gesture_spot_processsample(void *data, u16 len_bytes, struct gesture_struct *gesture)
{
    s16 *p = 0;

    if (unlikely(data == NULL || gesture == NULL || gs_init_flag == 0))
        return 0;

    if (unlikely(len_bytes != SAMPLE_SIZE_ITEMS * 2))
        // if (unlikely(len_bytes != SAMPLE_SIZE_ITEMS * sizeof(int)))
        return 0;

    p = (s16 *)data;
    mov_detect_calculate(p, gesture);

    if (unlikely(gesture->is_valid))
    {
        if (likely(use_template_matching_filtering))
        {
            if (!temp_match_apply(gesture, SAMPLE_SIZE_ITEMS))
                gesture->is_valid = 0;
        }
    }
    return gesture->is_valid;
}
//----------------------------------------------------------------------------Interface called by other function
int spotting_init_top(short *pbuf, int buf_size)
{
    // struct gs_data *my_data = (struct gs_data *)my->data_buf;
    struct template_entry t[2] = {{0, 15, 500, 1, 1}, {1, 2000, 6000, 1, 1}};
    struct mov_detect_struct_init m = {300, -1, 200, -1, 20, 15, 4};
    struct mov_detect_struct_init mB = {-1, -1, 100, -1, 5, 6, 1};

    gesture_spot_init(1000, t, 2, 1, &m, &mB, 1, 1, pbuf, buf_size);
    return 0;
}

int GestureSpotting_TopInterface(s16 ax, s16 ay, s16 az, s16 *pRetDataBuf, s16 *nLenInBytes)
{
    int flag_ret;
    static int TmpCount = 0;
    s16 data[3];
    struct gesture_struct gs;

    if (TmpCount == 0)
    {
        if (pRetDataBuf == NULL)
            return 0;
        spotting_init_top(pRetDataBuf, (300 * 3 * 2));
        TmpCount = 1;
    }

    data[0] = ax;
    data[1] = ay;
    data[2] = az;
    gesture_spot_processsample(data, sizeof(data), &gs);

    if (gs.is_valid == 1)
    {
        *nLenInBytes = gs.size_samples * sizeof(data);
        //*nLen = gs.size_samples * sizeof(data) + sizeof(u16);
        return 1;
    }
    else
    {
        return 0;
    }
}
