# Copyright (C) 2021, Mindee.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import os
import json
import tensorflow as tf
from typing import Tuple, List

__all__ = ["RecognitionDataset"]


class RecognitionDataset:
    """Data loader for recognition model

    Args:
        input_size: size (h, w) for the images
        img_folder: path to the images folder
        labels_path: pathe to the json file containing all labels (character sequences)
        batch_size: batch size to train on
        suffle: if True, dataset is shuffled between each epoch

    """
    def __init__(
        self,
        input_size: Tuple[int, int],
        img_folder: str,
        labels_path: str,
    ) -> None:
        self.input_size = input_size
        self.root = img_folder

        self.data: List[Tuple[str, Dict[str, Any]]] = []
        with open(labels_path) as f:
            labels = json.load(f)
        for img_path in os.listdir(self.root):
            label = labels.get(img_path)
            if not isinstance(label, str):
                raise KeyError("Image is not in referenced in label file")
            self.data.append((img_path, label))

    def __len__(self):
        return len(self.data)

    def __getitem__(
        self,
        index: int
    ) -> Tuple[tf.Tensor, List[str]]:

        img_name, label = self.data[index]
        img = tf.io.read_file(os.path.join(self.root, img_name))
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, self.input_size, method='bilinear')

        return img, label

    @staticmethod
    def collate_fn(samples):

        images, labels = zip(*samples)
        images = tf.stack(images, axis=0)

        return images, list(labels)