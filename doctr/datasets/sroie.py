# Copyright (C) 2021, Mindee.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import os
import csv
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple

from doctr.documents.reader import read_img
from doctr.models.utils import download_from_url
from .core import VisionDataset

__all__ = ['SROIE']


class SROIE(VisionDataset):
    """SROIE dataset from `"ICDAR2019 Competition on Scanned Receipt OCR and Information Extraction"
    <https://arxiv.org/pdf/2103.10213.pdf>`_.

    Example::
        >>> from doctr.datasets import SROIE
        >>> train_set = SROIE(train=True, download=True)
        >>> img, target = train_set[0]

    Args:
        train: whether the subset should be the training one
        **kwargs: keyword arguments from `VisionDataset`.
    """

    TRAIN = ('https://github.com/mindee/doctr/releases/download/v0.1.1/sroie2019_train_task1.zip',
             'd4fa9e60abb03500d83299c845b9c87fd9c9430d1aeac96b83c5d0bb0ab27f6f')
    TEST = ('https://github.com/mindee/doctr/releases/download/v0.1.1/sroie2019_test.zip',
            '41b3c746a20226fddc80d86d4b2a903d43b5be4f521dd1bbe759dbf8844745e2')

    def __init__(
        self,
        train: bool = True,
        **kwargs: Any,
    ) -> None:

        url, sha256 = self.TRAIN if train else self.TEST
        super().__init__(url, None, sha256, True, **kwargs)

        # # List images
        self.root = os.path.join(self._root, 'images')
        self.data: List[Tuple[str, List[Dict[str, Any]]]] = []
        for img_path in os.listdir(self.root):
            stem = Path(img_path).stem
            _targets = []
            with open(os.path.join(self._root, 'annotations', f"{stem}.txt"), encoding='latin') as f:
                for row in csv.reader(f, delimiter=','):
                    # Safeguard for blank lines
                    if len(row) > 0:
                        # Label may contain commas
                        label = ",".join(row[8:])
                        # Reduce 8 coords to 4
                        p1_x, p1_y, p2_x, p2_y, p3_x, p3_y, p4_x, p4_y = map(lambda x: int(x), row[:8])
                        left, right = min(p1_x, p2_x, p3_x, p4_x), max(p1_x, p2_x, p3_x, p4_x)
                        top, bot = min(p1_y, p2_y, p3_y, p4_y), max(p1_y, p2_y, p3_y, p4_y)
                        if len(label) > 0:
                            _targets.append((label, [left, top, right, bot]))

            text_targets, box_targets = zip(*_targets)

            self.data.append((img_path, dict(boxes=box_targets, labels=text_targets)))

    def __getitem__(self, index: int) -> Tuple[np.ndarray, Dict[str, Any]]:
        img_path, target = self.data[index]
        # Read image
        img = read_img(os.path.join(self.root, img_path))

        return img, target
