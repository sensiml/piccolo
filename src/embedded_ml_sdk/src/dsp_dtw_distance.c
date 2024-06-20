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




#include "kb_opt.h"

// FILL_ENABLE_DTW_DISTANCE
#ifdef ENABLE_DTW_DISTANCE

// FILL_MAX_WARP_LENGTH
#ifndef MAX_WARP_LENGTH
#define MAX_WARP_LENGTH 2048
#endif

int32_t globdist[MAX_WARP_LENGTH][MAX_WARP_LENGTH];
int32_t Dist[MAX_WARP_LENGTH][MAX_WARP_LENGTH];

unsigned short move[MAX_WARP_LENGTH][MAX_WARP_LENGTH];
unsigned short warp[2 * MAX_WARP_LENGTH][2];
unsigned short temp[2 * MAX_WARP_LENGTH][2];

#define DTW_DEBUG 0

int32_t get_distance_matrix_value(int32_t i, int32_t j)
{
    return Dist[i][j];
}

int32_t get_globdist(int32_t i, int32_t j)
{
    return globdist[i][j];
}

void compute_distance_matrix(unsigned char *x, unsigned char *y, int32_t x_size, int32_t y_size, uint8_t num_channels)
{
    /*Compute distance matrix*/
    int32_t i;
    int32_t j;
    int32_t k;
    int32_t channel_i_delta = 0;
    int32_t channel_j_delta = 0;
    int32_t total;

#if DTW_DEBUG
    printf("\nx = [");
    for (i = 0; i < x_size * num_channels; i++)
    {
        printf("%d, ", x[i]);
    }
    printf("]\ny = [");
    for (i = 0; i < y_size * num_channels; i++)
    {
        printf("%d, ", y[i]);
    }
    printf("]\n");
#endif
    if (num_channels > 1)
    {
        for (i = 0; i < x_size; i++)
        {
            channel_i_delta = num_channels * i;
            for (j = 0; j < y_size; j++)
            {
                channel_j_delta = num_channels * j;
                total = 0;
                for (k = 0; k < num_channels; k++)
                {
                    total = total + ((x[channel_i_delta + k] - y[channel_j_delta + k]) * (x[channel_i_delta + k] - y[channel_j_delta + k]));
                }
                Dist[i][j] = total;

#if DTW_DEBUG
                printf("Dist: %d %d %d\n", i, j, Dist[i][j]);
#endif
            }
        }
    }
    else
    {
        for (i = 0; i < x_size; i++)
        {
            for (j = 0; j < y_size; j++)
            {

                Dist[i][j] = ((x[i] - y[j]) * (x[i] - y[j]));

#if DTW_DEBUG
                printf("Dist: %d %d %d\n", i, j, Dist[i][j]);
#endif
            }
        }
    }
}

int32_t compute_warping_distance(int32_t x_size, int32_t y_size)
{
    int32_t i, j;

    int32_t top, mid, bot, cheapest;
    /*% for first frame, only possible match is at (0,0)*/

    int32_t warping_distance = Dist[x_size - 1][y_size - 1];

    globdist[0][0] = Dist[0][0];

    for (i = 1; i < x_size; i++)
    {
        globdist[i][0] = globdist[i - 1][0] + Dist[i][0];
    }

    for (j = 1; j < y_size; j++)
    {
        globdist[0][j] = globdist[0][j - 1] + Dist[0][j];
    }

    for (i = 1; i < x_size; i++)
    {
        for (j = 1; j < y_size; j++)
        {
            top = globdist[i - 1][j];     // Vert
            mid = globdist[i - 1][j - 1]; // diag
            bot = globdist[i][j - 1];     // Horiz

            if ((top < mid) && (top < bot) && top != mid)
            {
                cheapest = top;
            }
            else if (mid <= bot)
            {
                cheapest = mid;
            }
            else
            {
                cheapest = bot;
            }

            globdist[i][j] = cheapest + Dist[i][j];
        }
    }

    i = x_size - 1;
    j = y_size - 1;
    while (i > 0 || j > 0)
    {
        if (i == 0)
            j--;
        else if (j == 0)
            i--;
        else
        {
            top = globdist[i - 1][j];     // Vert
            mid = globdist[i - 1][j - 1]; // diag
            bot = globdist[i][j - 1];     // Horiz

            if ((top < mid) && (top < bot) && top != mid)
            {
                i--;
            }
            else if (mid <= bot)
            {
                j--;
                i--;
            }
            else
            {
                j--;
            }
        }

        warping_distance += Dist[i][j];

#if DTW_DEBUG
        printf("[%d][%d] = %d\n", i, j, warping_distance);
#endif
    }

    if (warping_distance > USHRT_MAX)
    {
        return USHRT_MAX;
    }

    return warping_distance;
}
#else

void compute_distance_matrix(unsigned char *x, unsigned char *y, int32_t x_size, int32_t y_size, uint8_t num_channels) {}
int32_t compute_warping_distance(int32_t x_size, int32_t y_size)
{
    return 0;
}
int32_t get_distance_matrix_value(int32_t i, int32_t j)
{
    return 0;
}

int32_t get_globdist(int32_t i, int32_t j)
{
    return 0;
}
#endif // USW_PME_DTW
