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

logger = logging.getLogger(__name__)


class FileType(str, Enum):
    YAML = "yaml"
    JSON = "json"
    JSONLD = "jsonld"
    PICKLE = "pkl"
    CSV = "csv"


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
        else:
            return None

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

    @classmethod
    def _open_pointer(cls, p, how, **kwargs):
        if how == FileType.PICKLE:
            r = pickle.load(p)
        elif how == FileType.YAML:
            r = yaml.load(p, Loader=yaml.FullLoader)
        elif how == FileType.JSON:
            r = json.load(p)
        elif how == FileType.JSONLD:
            r = [json.loads(s.decode()) for s in p.readlines()]
        elif how == FileType.JSONLD:
            r = pd.read_csv(p, **kwargs)
        else:
            r = dict()
        return r

    @classmethod
    def load(
        cls,
        how,
        ppath=None,
        pname=None,
        compression=None,
        fpath=None,
        **kwargs,
    ):
        if fpath is None:
            lemmas = pname.split(".")
            if lemmas[-1] == "gz":
                compression = "gz"
                how_ = cls._find_mode(lemmas[-2])
            else:
                how_ = cls._find_mode(lemmas[-1])
            if how_:
                how = how_
            bytes_ = pkgutil.get_data(ppath, pname)
        else:
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
        if compression == "gz":
            with gzip.GzipFile(fileobj=io.BytesIO(bytes_), mode="r") as p:
                r = cls._open_pointer(p, how, **kwargs)
        else:
            with io.BytesIO(bytes_) as p:
                r = cls._open_pointer(p, how, **kwargs)
        return r

    @classmethod
    def dump(cls, item, path, how="yaml"):
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
        if how == "pkl":
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
