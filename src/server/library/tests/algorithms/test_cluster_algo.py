"""
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
"""

from numpy import arange, pi, sin

from library.algorithms.clustering_algo import compute_distance


class TestClusterAlgo:
    def setup_class(self):
        Fs = sample = 110
        freq = 2
        x = arange(sample)
        y = sin(2 * pi * freq * x / Fs) + 1
        y = y * 100
        self.sine_signal_1 = [int(i) for i in (y[:100])]
        self.sine_signal_2 = [int(i) for i in (y[10:110])]

    def test_create_kb_description(self):
        distance = compute_distance(
            [self.sine_signal_1, self.sine_signal_2], "cityblock"
        )  # 'L1'
        assert distance[0] == 6544

        distance = compute_distance(
            [self.sine_signal_1, self.sine_signal_2], "chebyshev"
        )  # 'Lsup'
        assert distance[0] == 109

        distance = compute_distance([self.sine_signal_1, self.sine_signal_2], "DTW")
        assert distance[0] == 836
