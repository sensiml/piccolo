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




#include "mathcontext.h"
// #include "int_roots.h"
// #include "common_spotting.h"

#define INT_MIN 0x80000000
#define INT_MAX 0x7FFFFFFF

int m_sqrt(int x)
{
    return int_sqrt(x);
}

int m_mean(int *buffer, int length)
{
    int i;
    int32_t sum = 0;
    for (i = 0; i < length; ++i)
        sum += buffer[i];
    return (sum / length);
}

int m_var(int *data, int length)
{
    int i;
    int expx2 = 0;
    int expxU2 = 0;

    for (i = 0; i < length; ++i)
    {
        expxU2 = expxU2 + data[i];
        expx2 = expx2 + data[i] * data[i];
    }

    expxU2 = (expxU2 * expxU2) / (length * length);
    expx2 = expx2 / length;

    return (expx2 - expxU2);
}

int m_std(int *data, int length)
{
    return m_sqrt(m_var(data, length));
}

int m_max_min(int *buffer, int length, int *max, int *min)
{
    int i;
    *max = INT_MIN;
    *min = INT_MAX;
    for (i = 0; i < length; ++i)
    {
        if (*max < buffer[i])
            *max = buffer[i];
        if (*min > buffer[i])
            *min = buffer[i];
    }
    return 1;
}

int m_norm_sq(int *buffer, int length)
{
    int i;
    int32_t normsq = 0;
    for (i = 0; i < length; i++)
        normsq += (int)buffer[i] * buffer[i];
    return normsq;
}

unsigned int int_sqrt(unsigned int squared)
{
    static const unsigned int D[5] = {0, 268435456, 1073741824, 2415919104U, 4294967295U};
    static const unsigned int d[5] = {0, 16384, 32768, 49152, 65536};
    unsigned int P = 8192;
    unsigned int R = 67108864;
    unsigned int A = 0, a = 0, C = 0, c = 0, B = 0, b = 0, K = 0;

    B = squared;
    if (B >= D[4])
    {
        b = d[4];
        goto finish;
    }
    else if (B >= D[3])
    {
        if (B == D[3])
        {
            b = d[3];
            goto finish;
        }
        A = D[3];
        a = d[3];
        C = D[4];
        c = d[4];
    }
    else if (B >= D[2])
    {
        if (B == D[2])
        {
            b = d[2];
            goto finish;
        }
        A = D[2];
        a = d[2];
        C = D[3];
        c = d[3];
    }
    else if (B >= D[1])
    {
        if (B == D[1])
        {
            b = d[1];
            goto finish;
        }
        A = D[1];
        a = d[1];
        C = D[2];
        c = d[2];
    }
    else if (B >= D[0])
    {
        if (B == D[0])
        {
            b = d[0];
            goto finish;
        }
        A = D[0];
        a = d[0];
        C = D[1];
        c = d[1];
    }
    else
    {
        return -1;
    }

    while (1)
    {
        b = a + P;
        B = C - (C - A) / 2 - R;

        if (B == squared)
        {
            goto finish;
        }
        else if (B < squared)
        {
            A = B;
            a = b;
        }
        else
        {
            C = B;
            c = b;
        }

        if (c - a == 2)
        {
            K = (C - A) / 4;

            if (squared >= C - K)
            {
                b = c;
            }
            else if (squared < A + K)
            {
                b = a;
            }
            else
            {
                b = a + 1;
            }
            goto finish;
        }
        P /= 2;
        R /= 4;
    }

finish:
    return b;
}

uint32_t int_cbrt(uint64_t cubic)
{
    uint64_t left = cubic;
    uint64_t root = 1;
    int i, digits = 0;

    if (left == 0)
        return 0;

    while (left != 0)
    {
        digits++;
        left >>= 3;
    }

    /* Original algorithm is from "Nine Chapters on Arithmetic".
     * The improved algorithm is modify Decimal to Binary.
     */
    for (i = 1; i < digits; i++)
    {
        left = cubic >> ((digits - 1 - i) * 3);
        left -= (root << 1) * (root << 1) * (root << 1);
        if (left > (12 * root * root + 6 * root))
            root = (root << 1) + 1;
        else
            root <<= 1;
    }

    return root;
}
