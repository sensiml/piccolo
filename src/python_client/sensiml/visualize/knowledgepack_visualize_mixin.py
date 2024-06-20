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

import matplotlib.pyplot as plt


class VisualizeMixin:
    def plot_training_metrics(self, figsize=(16, 4)):
        """plots the loss and validation accuracy during training for a model"""
        if self.training_metrics:
            fig = plt.figure(figsize=figsize)
            num_iterations = len(self.training_metrics["loss"])
            plt.plot(self.training_metrics["accuracy"], label="training")
            plt.plot(self.training_metrics["val_accuracy"], label="validation")
            plt.xlabel("epochs")
            plt.ylabel("Accuracy")
            plt.xlim(0, num_iterations)
            plt.ylim(0, 1)
            plt.legend(loc="best")
            plt.show()
            fig = plt.figure(figsize=figsize)
            num_iterations = len(self.training_metrics["loss"])
            plt.plot(self.training_metrics["loss"], label="training")
            plt.plot(self.training_metrics["val_loss"], label="validation")
            plt.xlabel("epochs")
            plt.ylabel("Loss")
            plt.xlim(0, num_iterations)
            plt.legend(loc="best")
            plt.show()
        else:
            print("No training metrics for this model")
