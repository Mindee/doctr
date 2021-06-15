# Copyright (C) 2021, Mindee.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import torch
from torch import nn
from typing import Tuple, Dict, Any

from ...utils import conv_sequence, load_pretrained_params


__all__ = ['VGG', 'vgg16_bn']


default_cfgs: Dict[str, Dict[str, Any]] = {
    'vgg16_bn': {'num_blocks': (2, 2, 3, 3, 3), 'planes': (3, 64, 128, 256, 512, 512),
                 'rect_pools': (False, False, True, True, True),
                 'url': None},
}


class VGG(nn.Sequential):
    """Implements the VGG architecture from `"Very Deep Convolutional Networks for Large-Scale Image Recognition"
    <https://arxiv.org/pdf/1409.1556.pdf>`_.

    Args:
        num_blocks: number of convolutional block in each stage
        planes: number of output channels in each stage
        rect_pools: whether pooling square kernels should be replace with rectangular ones
        include_top: whether the classifier head should be added
        input_shape: shapes of the input tensor
    """
    def __init__(
        self,
        num_blocks: Tuple[int, int, int, int, int],
        planes: Tuple[int, int, int, int, int, int],
        rect_pools: Tuple[bool, bool, bool, bool, bool],
        include_top: bool = False,
        input_shape: Tuple[int, int, int] = (3, 512, 512),
    ) -> None:

        _layers = []
        # Specify input_shape only for the first layer
        kwargs = {"input_shape": input_shape}
        for nb_blocks, in_chan, out_chan, rect_pool in zip(num_blocks, planes[:-1], planes[1:], rect_pools):
            for _ in range(nb_blocks):
                _layers.extend([
                    nn.Conv2d(in_chan, out_chan, 3, padding=1, bias=False),
                    nn.BatchNorm2d(out_chan),
                    nn.ReLU(inplace=True),
                ])
                _layers.extend(conv_sequence(out_chan, 'relu', True, kernel_size=3, **kwargs))  # type: ignore[arg-type]
                kwargs = {}
            _layers.append(nn.MaxPool2d((2, 1 if rect_pool else 2)))
        if include_top:
            raise NotImplementedError
        super().__init__(_layers)


def _vgg(arch: str, pretrained: bool, **kwargs: Any) -> VGG:

    # Build the model
    model = VGG(default_cfgs[arch]['num_blocks'], default_cfgs[arch]['planes'],
                default_cfgs[arch]['rect_pools'], **kwargs)
    # Load pretrained parameters
    if pretrained:
        load_pretrained_params(model, default_cfgs[arch]['url'])

    return model


def vgg16_bn(pretrained: bool = False, **kwargs: Any) -> VGG:
    """VGG-16 architecture as described in `"Very Deep Convolutional Networks for Large-Scale Image Recognition"
    <https://arxiv.org/pdf/1409.1556.pdf>`_, modified by adding batch normalization.

    Example::
        >>> import torch
        >>> from doctr.models import vgg16_bn
        >>> model = vgg16_bn(pretrained=False)
        >>> input_tensor = torch.rand(1, 3, 224, 224)
        >>> out = model(input_tensor)

    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet

    Returns:
        VGG feature extractor
    """

    return _vgg('vgg16_bn', pretrained, **kwargs)
