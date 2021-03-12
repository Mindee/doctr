# Copyright (C) 2021, Mindee.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import os
import json
import hashlib
from zipfile import ZipFile
from pathlib import Path
from tensorflow.keras.utils import get_file
from typing import List, Dict, Any, Tuple

from doctr.models.utils import download_from_url
from .core import VisionDataset

__all__ = ['FUNSD']


class FUNSD(VisionDataset):
    """FUNSD dataset from `"FUNSD: A Dataset for Form Understanding in Noisy Scanned Documents"
    <https://arxiv.org/pdf/1905.13538.pdf>`_.

    Args:
        subset: subset of the dataset ('train' or 'test')
        download: whether the dataset should be downloaded if not present on disk
        overwrite: whether the archive should be re-extracted
    """

    URL = 'https://guillaumejaume.github.io/FUNSD/dataset.zip'
    SHA256 = 'c31735649e4f441bcbb4fd0f379574f7520b42286e80b01d80b445649d54761f'
    FILE_NAME = 'funsd.zip'

    def __init__(
        self,
        train: bool = True,
        **kwargs: Any,
    ) -> None:

        super().__init__(self.URL, self.FILE_NAME, self.SHA256, True, **kwargs)

        # Use the subset
        subfolder = os.path.join('dataset', 'training_data' if train else 'testing_data')

        # # List images
        self.root = os.path.join(self._root, subfolder, 'images')
        self.data: List[Tuple[str, List[Dict[str, Any]]]] = []
        for img_path in os.listdir(self.root):
            stem = Path(img_path).stem
            with open(os.path.join(self._root, subfolder, 'annotations', f"{stem}.json"), 'rb') as f:
                data = json.load(f)

            _targets = [(word['text'], word['box']) for block in data['form']
                        for word in block['words'] if len(word['text']) > 0]

            text_targets, box_targets = zip(*_targets)

            self.data.append((img_path, dict(boxes=box_targets, labels=text_targets)))

    def __getitem__(self, index: int) -> Tuple[str, Dict[str, Any]]:
        return self.data[index]
