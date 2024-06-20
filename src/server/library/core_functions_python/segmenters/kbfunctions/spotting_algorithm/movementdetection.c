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

#include "movementdetection.h"
#include "mathcontext.h"

#define MOT_DET_COUNT 45
#define MOT_DET_THRES 40

enum
{
    MD_UNKNOWN = -1,
    NOT_MOVING = 0,
    MAYBE_MOVING = 1,
    MOVING = 2,
    MAYBE_NOT_MOVING = 3,
};

struct mov_detect_struct
{
    s16 avgnotmovetomove[2];
    s16 stdnotmovetomove[2];
    s16 avgmovetonotmove[2];
    s16 stdmovetonotmove[2];

    u8 true_use_avg_false_use_std;
    u8 true_use_accel_false_use_gyro;

    s16 *buffer;
    int32_t sum;
    int32_t ssum;
    u16 window;
    u8 active;
    u16 num_pcount[2];
    u16 num_acount[2];
    u16 pcount[2];
    u16 acount[2];
    u16 nsample;
    u16 sample_index;
    u16 in_HF;
    u8 status;
};

enum
{
    NORMAL_THRES = 0,
    HIGH_THRES = 1
};

static s16 one_g_val;
static u8 during_gesture;
static struct gesture_struct current_data;
static struct mov_detect_struct md_couple[2];
static u8 use_f_b;
static u8 use_n_h;
static u16 current_data_index; /* samples during gesture to track current_data */
static u8 init_flag = 0;
static s8 adapt_para_count = 0;
#ifdef USE_BACKTRACKING
static s16 backtrack_queue[MAX_BACKTRACK_QUEUE_SIZE * 3];
static u8 is_backtrack_full;
static u16 backtrack_end;
#endif

u16 getavg(void);
u16 getstd(void);
void filtersample(s16 ax, s16 ay, s16 az);
int ismove(void);

u8 mov_detect_init(s16 one_g,
                   struct mov_detect_struct_init *m,
                   struct mov_detect_struct_init *m_h,
                   u8 use_forward_or_backward,
                   u8 _true_use_accel_false_use_gyro,
                   u8 _true_use_avg_false_use_std,
                   void *sample_buf,
                   int sample_buf_size)
{
    if (unlikely(m == NULL || sample_buf == NULL))
    {
        init_flag = 0;
        return init_flag;
    }

    one_g_val = one_g;
    use_f_b = use_forward_or_backward;
    use_n_h = HIGH_THRES;
    md_couple[use_f_b].window = m->window;
    md_couple[use_f_b].true_use_avg_false_use_std = _true_use_avg_false_use_std;
    md_couple[use_f_b].true_use_accel_false_use_gyro = _true_use_accel_false_use_gyro;
    md_couple[use_f_b].avgnotmovetomove[NORMAL_THRES] = m->avgnotmovetomove;
    md_couple[use_f_b].stdnotmovetomove[NORMAL_THRES] = m->stdnotmovetomove;
    md_couple[use_f_b].avgmovetonotmove[NORMAL_THRES] = m->avgmovetonotmove;
    md_couple[use_f_b].stdmovetonotmove[NORMAL_THRES] = m->stdmovetonotmove;
    md_couple[use_f_b].pcount[NORMAL_THRES] = m->ntimesmovingtonotmoving;
    md_couple[use_f_b].num_pcount[NORMAL_THRES] = m->ntimesmovingtonotmoving;
    md_couple[use_f_b].acount[NORMAL_THRES] = m->ntimesnotmovingtomoving;
    md_couple[use_f_b].num_acount[NORMAL_THRES] = m->ntimesnotmovingtomoving;
    md_couple[use_f_b].avgnotmovetomove[HIGH_THRES] = m_h->avgnotmovetomove;
    md_couple[use_f_b].stdnotmovetomove[HIGH_THRES] = m_h->stdnotmovetomove;
    md_couple[use_f_b].avgmovetonotmove[HIGH_THRES] = m_h->avgmovetonotmove;
    md_couple[use_f_b].stdmovetonotmove[HIGH_THRES] = m_h->stdmovetonotmove;
    md_couple[use_f_b].pcount[HIGH_THRES] = m_h->ntimesmovingtonotmoving;
    md_couple[use_f_b].num_pcount[HIGH_THRES] = m_h->ntimesmovingtonotmoving;
    md_couple[use_f_b].acount[HIGH_THRES] = m_h->ntimesnotmovingtomoving;
    md_couple[use_f_b].num_acount[HIGH_THRES] = m_h->ntimesnotmovingtomoving;
    md_couple[use_f_b].sum = 0;
    md_couple[use_f_b].ssum = 0;
    md_couple[use_f_b].nsample = 0;
    /* local accel samples buffer, 16 bits per sample */
    md_couple[use_f_b].buffer = (s16 *)ZMALLOC(2 * m->window, MEM_NORMAL);

    memset(md_couple[use_f_b].buffer, 0, 2 * m->window);

    md_couple[use_f_b].active = 0;
    md_couple[use_f_b].status = MD_UNKNOWN;

    current_data.sample = (s16 *)sample_buf;
    // ASSERT(sample_buf_size == MAX_CURRENT_DATA_SIZE_SAMPLES * SAMPLE_SIZE_ITEMS * 2);

#ifdef USE_BACKTRACKING
    is_backtrack_full = 0;
    backtrack_end = 0;
#endif

    init_flag = 1;
    return init_flag;
}

void mov_detect_startrec()
{
    during_gesture = 1;
    md_couple[use_f_b].active = 1;
    current_data_index = 0;
    current_data.is_valid = 0;
}

void mov_detect_stoprec(int gesture_ok)
{
    current_data.is_valid = gesture_ok;
    during_gesture = 0;
}

void mov_detect_calculate(s16 *data, struct gesture_struct *gesture)
{
#ifdef USE_BACKTRACKING
    u16 backtrack_size;
    u8 isbackmove;
    u16 bt_cnt;
    u16 i, j;
    s16 tmp_index;
    u16 increment;

    if (!during_gesture)
    {
        /* during gesture includes the period between strong threshold and forward threshold */
        backtrack_queue[backtrack_end++] = data[0];
        backtrack_queue[backtrack_end++] = data[1];
        backtrack_queue[backtrack_end++] = data[2];
        if (backtrack_end >= MAX_BACKTRACK_QUEUE_SIZE * SAMPLE_SIZE_ITEMS)
        {
            backtrack_end -= MAX_BACKTRACK_QUEUE_SIZE * SAMPLE_SIZE_ITEMS;
            is_backtrack_full = 1;
        }
    }
#endif
    use_f_b = USE_FORWARD;

    if (unlikely(data == NULL || gesture == NULL || init_flag == 0))
    {
        current_data.is_valid = 0;
        return;
    }

    filtersample(data[0], data[1], data[2]);

    if (ismove())
    {
        if (!during_gesture)
            /* here we start gesture and collecting gyro */
            mov_detect_startrec();
        else if (current_data_index < MAX_CURRENT_DATA_SIZE_SAMPLES)
            memcpy(&current_data.sample[current_data_index++ * SAMPLE_SIZE_ITEMS], data, SAMPLE_SIZE_ITEMS * 2);
    }
    else
    { /* not moving */
        if (during_gesture)
        { /* during gesture is true: end of gesture */
#ifdef USE_BACKTRACKING
            /* change to backward params, reset movement detector */
            use_f_b = USE_BACKWARD;
            md_couple[use_f_b].active = 1;
            md_couple[use_f_b].sum = 0;
            md_couple[use_f_b].ssum = 0;
            for (i = 0; i < md_couple[use_f_b].window; i++)
            {
                md_couple[use_f_b].buffer[i] = md_couple[use_f_b].avgmovetonotmove[use_n_h] + 1;
                md_couple[use_f_b].sum += md_couple[use_f_b].buffer[i];
                md_couple[use_f_b].ssum += md_couple[use_f_b].buffer[i] * md_couple[use_f_b].buffer[i];
            }
            /* detect movement */
            backtrack_size = is_backtrack_full ? MAX_BACKTRACK_QUEUE_SIZE : (backtrack_end / SAMPLE_SIZE_ITEMS);
            tmp_index = backtrack_end;
            for (bt_cnt = 0; bt_cnt < backtrack_size; bt_cnt++)
            {
                if (tmp_index <= 0)
                    tmp_index += MAX_BACKTRACK_QUEUE_SIZE * SAMPLE_SIZE_ITEMS;
                filtersample(backtrack_queue[tmp_index - SAMPLE_SIZE_ITEMS], backtrack_queue[tmp_index - (SAMPLE_SIZE_ITEMS - 1)], backtrack_queue[tmp_index - (SAMPLE_SIZE_ITEMS - 2)]);
                tmp_index = tmp_index - SAMPLE_SIZE_ITEMS;
                isbackmove = ismove();
                if (isbackmove == 0)
                    ; //;break
            }
            if (bt_cnt != backtrack_size)
                bt_cnt++;

            /* add backtrack data to current data */
            increment = SAMPLE_SIZE_ITEMS * bt_cnt;
            for (i = 0; i < current_data_index; i++)
            {
                tmp_index = current_data_index * SAMPLE_SIZE_ITEMS - SAMPLE_SIZE_ITEMS * i;
                for (j = 1; j < SAMPLE_SIZE_ITEMS + 1; j++)
                {
                    if (tmp_index + increment - j < MAX_CURRENT_DATA_SIZE_SAMPLES * SAMPLE_SIZE_ITEMS - 1)
                        current_data.sample[tmp_index + increment - j] = current_data.sample[tmp_index - j];
                }
            }
            current_data_index = current_data_index + increment / SAMPLE_SIZE_ITEMS;
            if (current_data_index > MAX_CURRENT_DATA_SIZE_SAMPLES)
                current_data_index = MAX_CURRENT_DATA_SIZE_SAMPLES;
            tmp_index = backtrack_end - bt_cnt * SAMPLE_SIZE_ITEMS;
            if (tmp_index < 0)
                tmp_index += MAX_BACKTRACK_QUEUE_SIZE * SAMPLE_SIZE_ITEMS;
            else if (tmp_index >= MAX_BACKTRACK_QUEUE_SIZE * SAMPLE_SIZE_ITEMS)
                tmp_index -= MAX_BACKTRACK_QUEUE_SIZE * SAMPLE_SIZE_ITEMS;
            for (i = 0; i < bt_cnt; i++)
            {
                for (j = 0; j < SAMPLE_SIZE_ITEMS; j++)
                {
                    if (tmp_index + i * SAMPLE_SIZE_ITEMS + j >= MAX_BACKTRACK_QUEUE_SIZE * SAMPLE_SIZE_ITEMS)
                        current_data.sample[i * SAMPLE_SIZE_ITEMS + j] = backtrack_queue[tmp_index + i * SAMPLE_SIZE_ITEMS + j - MAX_BACKTRACK_QUEUE_SIZE * SAMPLE_SIZE_ITEMS];
                    else
                        current_data.sample[i * SAMPLE_SIZE_ITEMS + j] = backtrack_queue[tmp_index + i * SAMPLE_SIZE_ITEMS + j];
                }
            }

            /* reset, and change to forward params */
            is_backtrack_full = 0;
            backtrack_end = 0;
            use_f_b = USE_FORWARD;
#endif
            mov_detect_stoprec(during_gesture);
        }
        else
        { /* during_gesture = false: no movement, no gesture */
            current_data.is_valid = 0;
            if (getstd() > MOT_DET_THRES)
            {
                if (adapt_para_count < 0)
                    adapt_para_count = 1;
                else
                    adapt_para_count++;
            }
            else
            {
                if (adapt_para_count > 0)
                    adapt_para_count = -1;
                else
                    adapt_para_count--;
            }
            if (adapt_para_count > MOT_DET_COUNT)
            {
                use_n_h = HIGH_THRES;
                adapt_para_count = 0;
            }
            else if (adapt_para_count < -MOT_DET_COUNT)
            {
                use_n_h = NORMAL_THRES;
                adapt_para_count = 0;
            }
        }
    }

    current_data.size_samples = current_data_index;
    *gesture = current_data;
}

void filtersample(s16 ax, s16 ay, s16 az)
{
    u16 in;

    if (likely(md_couple[use_f_b].true_use_avg_false_use_std))
        in = (int)m_abs(m_sqrt(ax * ax + ay * ay + az * az) - one_g_val);
    else
        in = (int)m_abs(m_sqrt(ax * ax + ay * ay + az * az));

#define SAMPLEIDX md_couple[use_f_b].nsample
    md_couple[use_f_b].in_HF = in;
    md_couple[use_f_b].sum = md_couple[use_f_b].sum - md_couple[use_f_b].buffer[SAMPLEIDX];
    md_couple[use_f_b].ssum = md_couple[use_f_b].ssum - (md_couple[use_f_b].buffer[SAMPLEIDX] * md_couple[use_f_b].buffer[SAMPLEIDX]);
    md_couple[use_f_b].sum = md_couple[use_f_b].sum + in;
    md_couple[use_f_b].ssum = md_couple[use_f_b].ssum + (in * in);
    md_couple[use_f_b].buffer[SAMPLEIDX] = in;
    SAMPLEIDX++;

    if (SAMPLEIDX >= md_couple[use_f_b].window)
        SAMPLEIDX = 0;
}

int ismove()
{
    int avg;
    if (likely(md_couple[use_f_b].true_use_avg_false_use_std))
    {
        avg = getavg();
    }
    else
        avg = getstd();

    if (avg > md_couple[use_f_b].avgnotmovetomove[use_n_h] && !md_couple[use_f_b].active)
    {
        md_couple[use_f_b].status = MAYBE_MOVING;

        if (md_couple[use_f_b].acount[use_n_h]-- == 0)
        {
            md_couple[use_f_b].status = MOVING;
            md_couple[use_f_b].active = 1;
            md_couple[use_f_b].acount[use_n_h] = md_couple[use_f_b].num_acount[use_n_h];
        }
    }
    else if (avg < md_couple[use_f_b].avgmovetonotmove[use_n_h] && md_couple[use_f_b].active)
    {
        /* forward threshold or backward threshold */
        md_couple[use_f_b].status = MAYBE_NOT_MOVING;

        if (md_couple[use_f_b].pcount[use_n_h]-- == 0)
        {
            md_couple[use_f_b].status = NOT_MOVING;
            md_couple[use_f_b].active = 0;
            md_couple[use_f_b].pcount[use_n_h] = md_couple[use_f_b].num_pcount[use_n_h];
        }
    }
    else
    {
        md_couple[use_f_b].acount[use_n_h] = md_couple[use_f_b].num_acount[use_n_h];
        md_couple[use_f_b].pcount[use_n_h] = md_couple[use_f_b].num_pcount[use_n_h];
    }

    return md_couple[use_f_b].active;
}

u16 getavg()
{
    /* md_couple[use_f_b].window = 20, can't change division to shift */
    return (u16)m_abs((md_couple[use_f_b].sum / md_couple[use_f_b].window));
}

u16 getstd()
{
    /* md_couple[use_f_b].window = 20, can't change division to shift */
    s16 avg = md_couple[use_f_b].sum / md_couple[use_f_b].window;
    u16 stddev = (u16)m_sqrt((md_couple[use_f_b].ssum + md_couple[use_f_b].window * avg * avg - 2 * md_couple[use_f_b].sum * avg) / md_couple[use_f_b].window);
    return stddev;
}
