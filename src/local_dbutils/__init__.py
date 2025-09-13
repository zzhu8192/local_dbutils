from __future__ import annotations

from .fs import DBUtilsFS


class DBUtils:
    """Local, Linux-only dbutils shim.

    Focuses on dbutils.fs-compatible behavior on the local filesystem.
    Paths beginning with `dbfs:/` are mapped to a local root directory.
    Configure root via env var `DBUTILS_DBFS_ROOT` (defaults to `./dbfs`).
    """

    def __init__(self) -> None:
        self.fs = DBUtilsFS()


# Convenience singleton mirroring Databricks' `dbutils`
dbutils = DBUtils()

__all__ = ["DBUtils", "dbutils", "DBUtilsFS"]

