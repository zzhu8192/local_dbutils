from __future__ import annotations

import os
from pathlib import Path

import pytest

from local_dbutils import dbutils


def test_dbfs_root_env(tmp_path, monkeypatch):
    monkeypatch.setenv("DBUTILS_DBFS_ROOT", str(tmp_path / "dbfsroot"))
    db_path = "dbfs:/data"
    assert dbutils.fs.mkdirs(db_path)
    p = tmp_path / "dbfsroot" / "data"
    assert p.exists() and p.is_dir()


def test_put_head_tail_ls_rm(tmp_path, monkeypatch):
    monkeypatch.setenv("DBUTILS_DBFS_ROOT", str(tmp_path / "dbfsroot"))
    fpath = "dbfs:/folder/hello.txt"
    dbutils.fs.put(fpath, "hello world", overwrite=True)
    # head/tail
    assert dbutils.fs.head(fpath, max_bytes=5) == "hello"
    assert dbutils.fs.tail(fpath, max_bytes=5) == "world"
    # ls
    items = dbutils.fs.ls("dbfs:/folder")
    assert any(i.name == "hello.txt" for i in items)
    # rm
    assert dbutils.fs.rm("dbfs:/folder", recurse=True)
    assert not (tmp_path / "dbfsroot" / "folder").exists()


def test_cp_mv(tmp_path, monkeypatch):
    monkeypatch.setenv("DBUTILS_DBFS_ROOT", str(tmp_path / "dbfsroot"))
    src = Path(tmp_path / "dbfsroot" / "src")
    (src / "a").mkdir(parents=True)
    (src / "a" / "f.txt").write_text("X")
    # copy dir requires recurse
    dest = "dbfs:/dst"
    with pytest.raises(IsADirectoryError):
        dbutils.fs.cp("dbfs:/src", dest)
    assert dbutils.fs.cp("dbfs:/src", dest, recurse=True)
    assert (tmp_path / "dbfsroot" / "dst" / "a" / "f.txt").exists()
    # move file
    assert dbutils.fs.mv("dbfs:/dst/a/f.txt", "dbfs:/dst/a/g.txt")
    assert not (tmp_path / "dbfsroot" / "dst" / "a" / "f.txt").exists()
    assert (tmp_path / "dbfsroot" / "dst" / "a" / "g.txt").exists()

