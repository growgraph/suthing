import gzip
import io
import json
import logging
import pickle
import pkgutil
from enum import Enum
from os.path import expanduser

import pandas as pd
import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class FileType(str, Enum):
    YAML = "yaml"
    JSON = "json"
    JSONLD = "jsonld"
    PICKLE = "pkl"
    CSV = "csv"
    TXT = "txt"
    ENV = "env"


class FileHandle:
    @classmethod
    def _find_mode(cls, lemma):
        if lemma in ["yml", "yaml"]:
            return FileType.YAML
        elif lemma == "json":
            return FileType.JSON
        elif lemma == "jsonld":
            return FileType.JSONLD
        elif lemma in ["pkl", "pickle"]:
            return FileType.PICKLE
        elif lemma in ["csv"]:
            return FileType.CSV
        elif lemma in ["env"]:
            return FileType.ENV
        else:
            return FileType.TXT

    @classmethod
    def _dump_pointer(cls, item, p, how, bytes_=True):
        if how == FileType.PICKLE:
            pickle.dump(item, p, pickle.HIGHEST_PROTOCOL)
        elif how == FileType.YAML:
            yc = yaml.dump(item)
            if bytes_:
                yc = yc.encode("utf-8")
            p.write(yc)
        elif how == FileType.JSON:
            jc = json.dumps(item, indent=2) + "\n"
            if bytes_:
                jc = jc.encode("utf-8")
            p.write(jc)
        elif how == FileType.JSONLD:
            for subitem in item:
                jc = json.dumps(subitem) + "\n"
                if bytes_:
                    jc = jc.encode("utf-8")
                p.write(jc)
        elif how == FileType.CSV and (
            isinstance(item, pd.DataFrame) or isinstance(item, pd.Series)
        ):
            r = item.to_csv()
            if bytes_:
                r = r.encode("utf-8")
            p.write(r)
        elif how == FileType.TXT:
            p.write(str(item))

    @classmethod
    def _open_pointer(
        cls, p: io.BytesIO | gzip.GzipFile, how: FileType, **kwargs
    ):
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
                raise ValueError(f"Will not read gzipped env files")
        else:
            r = dict()
        return r

    @classmethod
    def load(
        cls,
        ppath=None,
        pname=None,
        how: FileType = FileType.YAML,
        **kwargs,
    ):
        compression = kwargs.pop("compression", None)
        fpath = kwargs.pop("fpath", None)

        # interpret as package load
        if pname is not None:
            lemmas = pname.split(".")
            if lemmas[-1] == "gz":
                compression = "gz"
                how_ = cls._find_mode(lemmas[-2])
            else:
                how_ = cls._find_mode(lemmas[-1])
            if how_:
                how = how_
            bytes_ = pkgutil.get_data(ppath, pname)

        # interpret as filesystem load
        else:
            if fpath is None:
                fpath = ppath
            fpath = expanduser(fpath)
            lemmas = fpath.split(".")
            if lemmas[-1] == "gz":
                compression = "gz"
                how_ = cls._find_mode(lemmas[-2])
            else:
                how_ = cls._find_mode(lemmas[-1])
            if how_:
                how = how_
            with open(fpath, "rb") as fp:
                bytes_ = fp.read()

        if bytes_ is None:
            raise ValueError(f"None received as Bytes")

        if compression == "gz":
            with gzip.GzipFile(fileobj=io.BytesIO(bytes_), mode="r") as p:
                r = cls._open_pointer(p, how, **kwargs)
        else:
            with io.BytesIO(bytes_) as p:
                r = cls._open_pointer(p, how, **kwargs)
        return r

    @classmethod
    def dump(cls, item, path, how: FileType = FileType.YAML):
        """

        :param item:
        :param path: if path ends with ".gz" the output will be gzip compressed
        :param how:
        :return:
        """
        lemmas = path.split(".")
        path = expanduser(path)
        if lemmas[-1] == "gz":
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
