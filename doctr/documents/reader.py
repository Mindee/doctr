# Copyright (C) 2021, Mindee.
# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import os
import fitz
import magic
import numpy as np
import pathlib
import cv2
import warnings
from typing import Union, List, Tuple, Optional

ALLOWED_PDF = ["application/pdf"]
DEFAULT_RES_MIN = 0.8e6
DEFAULT_RES_MAX = 3e6


def document_reader(
    filepaths: Union[List[str], str], 
    pdf_resolution: Optional[Union[int, Tuple[int, int], float, Tuple[float, float]]]=None
    ) -> Tuple[List[List[List[int]]], List[List[bytes]], List[List[str]]]:
    """
    :param filepaths: list of filepaths or filepaths
    :param pdf_resolution: resolution for the outputs images
    """
    documents_imgs, documents_names = prepare_pdf_documents(
        filepaths=filepaths, pdf_resolution=pdf_resolution)
    shapes = [[page.shape[:2] for page in doc] for doc in documents_imgs]
    raw_images = [[page.flatten().tostring() for page in doc] for doc in documents_imgs]

    return shapes, raw_images, documents_names


def prepare_pdf_documents(
    filepaths: Union[List[str], str]=None, 
    pdf_resolution: Optional[Union[int, Tuple[int, int], float, Tuple[float, float]]]=None
    ) -> Tuple[List[List[np.ndarray]], List[List[str]]]:
    """
    Always return tuple of:
        - list of documents, each doc is a numpy image pages list (valid RGB image with 3 channels)
        - list of document names, each page inside a doc has a different name
    optional : list of sizes
    :param filepaths: list of pdf filepaths to prepare, or a filepath (str)
    :param pdf_resolution: output resolution of images
    :param with_sizes: to return the list of sizes
    """

    if filepaths is None:
        raise Exception

    documents_imgs = []
    documents_names = []

    # make document dimension if not existing:
    if isinstance(filepaths, str):
        filepaths = [filepaths]

    for f_document in filepaths:

        size = os.path.getsize(f_document)
        pages_imgs, pages_names = prepare_pdf_from_filepath(
            f_document, pdf_resolution=pdf_resolution
        )

        documents_imgs.append(pages_imgs)
        documents_names.append(pages_names)
    
    return documents_imgs, documents_names


def prepare_pdf_from_filepath(filepath: str, 
    pdf_resolution: Optional[Union[int, Tuple[int, int], float, Tuple[float, float]]]=None
    ) -> Tuple[List[np.ndarray], List[str]]:
    """
    Read a pdf from a filepath with fitz
    :param filepath: filepath of the .pdf file
    :param pdf_resolution: output resolution
    """

    if not os.path.isfile(filepath):
        raise FileNotFoundError

    filename = pathlib.PurePosixPath(filepath).stem

    mimetype = magic.from_file(filepath, True)

    if mimetype in ALLOWED_PDF:
        pdf = fitz.open(filepath)
        imgs, names = convert_pdf_pages_to_imgs(
            pdf=pdf, filename=filename, page_idxs=None, resolution=pdf_resolution)
        return imgs, names

    else:
        raise TypeError('not a pdf')


def convert_pdf_pages_to_imgs(
    pdf: fitz.fitz.Document,
    filename:str,
    page_idxs: Optional[Union[List[int], int]],
    resolution: Optional[Union[int, Tuple[int, int], float, Tuple[float, float]]]=None,
    img_type: str="np"
    ) -> Tuple[List[np.ndarray], List[str]]:
    """
    Convert pdf pages to numpy arrays.
    :param pdf: pdf doc opened with fitz
    :param filename: pdf name to rename pages
    :param img_type: The format of the output pages, can be "np" or "png"
    :param page_idxs: Int or list of int to specify which pages to take. If None, takes all pages.
    :param resolution: Output resolution in pixels. If None, use the default page size (DPI@96).
    Can be used as a tuple to force a minimum/maximum resolution dynamically.
    :param with_names: Output list of names in return statement.
    :return: List of numpy arrays of dtype uint8.
    """

    imgs = []
    names = []

    # Decode pages parameter
    if isinstance(page_idxs, int):
        page_idxs = [page_idxs]
    page_idxs = page_idxs or [x + 1 for x in range(len(pdf))]

    # Iterate over pages
    for i in page_idxs:

        page = pdf[i-1]

        # set resolution
        if isinstance(resolution, tuple):
            out_res = int(resolution[0] * resolution[1])
        else:
            out_res = max(min(int(resolution), DEFAULT_RES_MAX), 
            DEFAULT_RES_MIN) if isinstance(resolution, Union[int, float].__args__) else None

        # Make numpy array
        pixmap = page_to_pixmap(page, out_res)

        if img_type == "np":
            imgs.append(pixmap_to_numpy(pixmap))
        else:
            if img_type != "png":
                warnings.warn(f"could not convert to {img_type}, returning png")
            imgs.append(pixmap.getImageData(output="png"))

    names = [f"{filename}-p{str(idx).zfill(3)}" for idx in page_idxs]

    return imgs, names


def page_to_pixmap(
    page: fitz.fitz.Page, 
    resolution: Optional[Union[int, Tuple[int, int], float, Tuple[float, float]]]=None
    ) -> fitz.fitz.Pixmap:
    """
    Convert a fitz page to a fitz bitmap
    """
    out_res = resolution
    scale = 1   
    if out_res:
        box = page.MediaBox
        in_res = int(box[2]) * int(box[3])
        scale = min(20, out_res / in_res)  # to prevent error if in_res is very low
    return page.getPixmap(matrix=fitz.Matrix(scale, scale))


def pixmap_to_numpy(
    pixmap: fitz.fitz.Pixmap,
    channel_order: str="RGB"
    ) -> np.ndarray:
    """
    convert a fitz pixmap to a numpy image
    """
    stream = pixmap.getImageData()
    stream = np.frombuffer(stream, dtype=np.uint8)
    img = cv2.imdecode(stream, cv2.IMREAD_UNCHANGED)
    if channel_order == "RGB":
        return img[:, :, ::-1]
    elif channel_order == "BGR":
        return img
    else:
        raise Exception("Invalid channel parameter! Must be RGB or BGR")


