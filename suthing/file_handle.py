"""Utilities for handling different file types and formats.

This module provides a flexible interface for reading and writing various file formats
including YAML, JSON, CSV, pickle and others. Supports both regular and gzipped files.
"""

import gzip
import io
import json
import logging
import pathlib
import pickle
import pkgutil
from enum import Enum

import pandas as pd
import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def suffixes(fp: str | pathlib.Path):
    """Extract file suffixes from a path.

    Args:
        fp: File path as string or Path object

    Returns:
        List of suffix strings
    """
    if isinstance(fp, str):
        fp = pathlib.Path(fp)
    suffixes = fp.suffixes
    if not suffixes and "." in fp.stem:
        return [fp.stem]
    return fp.suffixes


class FileType(str, Enum):
    """Supported file types for reading and writing."""

    YAML = "yaml"
    JSON = "json"
    JSONLD = "jsonld"
    PICKLE = "pkl"
    CSV = "csv"
    TXT = "txt"
    ENV = "env"


class FileHandle:
    """Main class for handling file operations across different formats."""

    @classmethod
    def _find_mode(cls, lemma: str):
        """Determine file type from file extension.

        Args:
            lemma: File extension string

        Returns:
            FileType enum value corresponding to the extension
        """
        if lemma in [".yml", ".yaml"]:
            return FileType.YAML
        elif lemma == ".json":
            return FileType.JSON
        elif lemma == ".jsonld":
            return FileType.JSONLD
        elif lemma in [".pkl", ".pickle"]:
            return FileType.PICKLE
        elif lemma in [".csv"]:
            return FileType.CSV
        elif lemma in [".env"]:
            return FileType.ENV
        else:
            return FileType.TXT

    @classmethod
    def _dump_pointer(cls, item, p, how: FileType, bytes_: bool = True) -> None:
        """Write data to file pointer in specified format.

        Args:
            item: Data to write
            p: File pointer
            how: FileType indicating format to write in
            bytes_: Whether to write in bytes mode
        """
        if how == FileType.PICKLE:
            pickle.dump(item, p, pickle.HIGHEST_PROTOCOL)
        elif how == FileType.YAML:
            yc = yaml.dump(item)
            if bytes_:
                yc = yc.encode("utf-8")  # type: ignore
            p.write(yc)
        elif how == FileType.JSON:
            jc = json.dumps(item, indent=2) + "\n"
            if bytes_:
                jc = jc.encode("utf-8")  # type: ignore
            p.write(jc)
        elif how == FileType.JSONLD:
            for subitem in item:
                jc = json.dumps(subitem) + "\n"
                if bytes_:
                    jc = jc.encode("utf-8")  # type: ignore
                p.write(jc)
        elif how == FileType.CSV and (
            isinstance(item, pd.DataFrame) or isinstance(item, pd.Series)
        ):
            r = item.to_csv()
            if bytes_:
                r = r.encode("utf-8")  # type: ignore
            p.write(r)
        elif how == FileType.TXT:
            p.write(str(item))

    @classmethod
    def _open_pointer(cls, p: io.BytesIO | gzip.GzipFile, how: FileType, **kwargs):
        """Read data from file pointer in specified format.

        Args:
            p: File pointer
            how: FileType indicating format to read
            **kwargs: Additional arguments passed to readers

        Returns:
            Data read from file in appropriate format

        Raises:
            ValueError: If trying to read gzipped env files
        """
        if how == FileType.PICKLE:
            r = pickle.load(p)
        elif how == FileType.YAML:
            r = yaml.load(p, Loader=yaml.FullLoader)
        elif how == FileType.JSON:
            r = json.load(p)
        elif how == FileType.JSONLD:
            r = [json.loads(s.decode()) for s in p.readlines()]
        elif how == FileType.CSV:
            r = pd.read_csv(p, **kwargs)  # type: ignore[arg-type]
        elif how == FileType.TXT:
            r = p.read().decode()
        elif how == FileType.ENV:
            if isinstance(p, io.BytesIO):
                config = io.StringIO(p.getvalue().decode("UTF-8"))
                r = load_dotenv(stream=config)
            else:
                raise ValueError("Will not read gzipped env files")
        else:
            r = dict()
        return r

    @classmethod
    def load(
        cls,
        ppath: str | pathlib.Path | None = None,
        pname: str | None = None,
        how: FileType = FileType.YAML,
        **kwargs,
    ):
        """

        :param ppath:
        :param pname:
        :param how:
        :param kwargs:
        :return:
        """

        compression = kwargs.pop("compression", None)
        fpath: str | pathlib.Path | None = kwargs.pop("fpath", None)

        # assume loading from a package
        if pname is not None:
            lemmas = suffixes(pname)
            if lemmas[-1] == ".gz":
                compression = "gz"
                how_ = cls._find_mode(lemmas[-2])
            else:
                how_ = cls._find_mode(lemmas[-1])
            if how_:
                how = how_
            if ppath is not None and isinstance(ppath, str):
                bytes_ = pkgutil.get_data(ppath, pname)
            else:
                raise ValueError(
                    "package name provided, package path (as a string) needed"
                )

        # interpret as filesystem load
        else:
            if fpath is None:
                if ppath is not None:
                    fpath = ppath
                else:
                    raise ValueError("either fpath or ppath should be provided")
            fpath = pathlib.Path(fpath).expanduser().as_posix()
            lemmas = suffixes(fpath)
            if lemmas[-1] == ".gz":
                compression = "gz"
                how_ = cls._find_mode(lemmas[-2])
            else:
                how_ = cls._find_mode(lemmas[-1])
            if how_:
                how = how_
            with open(fpath, "rb") as fp:
                bytes_ = fp.read()

        if bytes_ is None:
            raise ValueError("None received as Bytes")

        if compression == "gz":
            with gzip.GzipFile(fileobj=io.BytesIO(bytes_), mode="r") as p:
                r = cls._open_pointer(p, how, **kwargs)
        else:
            with io.BytesIO(bytes_) as p:
                r = cls._open_pointer(p, how, **kwargs)
        return r

    @classmethod
    def dump(cls, item, path: str | pathlib.Path, how: FileType = FileType.YAML):
        """

        :param item:
        :param path: if path ends with ".gz" the output will be gzip compressed
        :param how:
        :return:
        """

        lemmas = suffixes(path)
        path = pathlib.Path(path).expanduser().as_posix()
        if lemmas[-1] == ".gz":
            compression = "gz"
            how_ = cls._find_mode(lemmas[-2])
        else:
            compression = None
            how_ = cls._find_mode(lemmas[-1])
        if how_:
            how = how_
        if how == FileType.PICKLE:
            mode = "wb"
        else:
            mode = "w"
        if compression == "gz":
            if not path.endswith(".gz"):
                path += ".gz"
            with gzip.GzipFile(path, mode=mode) as p:
                cls._dump_pointer(item, p, how)
        else:
            with open(path, mode=mode) as p:
                cls._dump_pointer(item, p, how, bytes_=False)
