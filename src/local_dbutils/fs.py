from __future__ import annotations

import io
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


def _dbfs_root() -> Path:
    root = os.environ.get("DBUTILS_DBFS_ROOT", "dbfs")
    p = Path(root)
    p.mkdir(parents=True, exist_ok=True)
    return p.resolve()


def _resolve_path(path: str | os.PathLike[str]) -> Path:
    """Resolve dbutils-style paths to local filesystem paths.

    Supported schemes:
    - dbfs:/...  -> maps under local `_dbfs_root()`
    - file:/...  -> local absolute path
    - / or relative path -> interpreted relative to CWD
    """
    s = str(path)
    if s.startswith("dbfs:/"):
        rel = s[len("dbfs:/"):].lstrip("/")
        return _dbfs_root() / rel
    if s.startswith("file:/"):
        # Treat file:/ as absolute POSIX path
        return Path(s[len("file:"):])
    return Path(s)


@dataclass(frozen=True)
class FileInfo:
    path: str
    name: str
    size: int
    modification_time: Optional[float] = None


class DBUtilsFS:
    """Local filesystem implementation of Databricks `dbutils.fs`.

    Methods intentionally mirror the Databricks interface where practical.
    All paths may be plain local paths, `file:/...`, or `dbfs:/...`.
    """

    # ---------- Discovery ----------
    def ls(self, path: str | os.PathLike[str]) -> List[FileInfo]:
        p = _resolve_path(path)
        if not p.exists():
            raise FileNotFoundError(f"Path not found: {path}")
        if not p.is_dir():
            # For parity, listing a file returns its info
            stat = p.stat()
            return [
                FileInfo(
                    path=str(path),
                    name=p.name,
                    size=stat.st_size,
                    modification_time=stat.st_mtime,
                )
            ]
        items: List[FileInfo] = []
        for child in sorted(p.iterdir(), key=lambda c: c.name):
            stat = child.stat()
            size = stat.st_size if child.is_file() else 0
            # Report the original scheme path for better UX
            child_display = self._to_scheme_path(child)
            items.append(
                FileInfo(
                    path=child_display,
                    name=child.name,
                    size=size,
                    modification_time=stat.st_mtime,
                )
            )
        return items

    # ---------- Mutation ----------
    def mkdirs(self, path: str | os.PathLike[str]) -> bool:
        p = _resolve_path(path)
        p.mkdir(parents=True, exist_ok=True)
        return True

    def rm(self, path: str | os.PathLike[str], recurse: bool = False) -> bool:
        p = _resolve_path(path)
        if not p.exists():
            return False
        if p.is_dir():
            if recurse:
                shutil.rmtree(p)
                return True
            # Only remove empty dir if not recurse
            try:
                p.rmdir()
                return True
            except OSError as exc:  # not empty
                raise IsADirectoryError(
                    f"Directory not empty: {path}. Use recurse=True."
                ) from exc
        else:
            p.unlink()
            return True

    def cp(self, src: str | os.PathLike[str], dst: str | os.PathLike[str], recurse: bool = False) -> bool:
        src_p = _resolve_path(src)
        dst_p = _resolve_path(dst)
        if not src_p.exists():
            raise FileNotFoundError(f"Source not found: {src}")
        if src_p.is_dir():
            if not recurse:
                raise IsADirectoryError("Source is a directory. Use recurse=True.")
            if dst_p.exists() and dst_p.is_file():
                raise NotADirectoryError("Cannot copy directory into a file destination.")
            if dst_p.exists():
                # Copy contents under existing dir target
                for child in src_p.iterdir():
                    self.cp(child, dst_p / child.name, recurse=True)
                return True
            shutil.copytree(src_p, dst_p)
            return True
        # src is file
        dst_p.parent.mkdir(parents=True, exist_ok=True)
        if dst_p.exists() and dst_p.is_dir():
            shutil.copy2(src_p, dst_p / src_p.name)
        else:
            shutil.copy2(src_p, dst_p)
        return True

    def mv(self, src: str | os.PathLike[str], dst: str | os.PathLike[str], recurse: bool = False) -> bool:
        src_p = _resolve_path(src)
        dst_p = _resolve_path(dst)
        if not src_p.exists():
            raise FileNotFoundError(f"Source not found: {src}")
        if src_p.is_dir() and not recurse:
            raise IsADirectoryError("Source is a directory. Use recurse=True.")
        dst_p.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_p), str(dst_p))
        return True

    def put(self, path: str | os.PathLike[str], contents: str, overwrite: bool = False) -> None:
        p = _resolve_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists() and not overwrite:
            raise FileExistsError(f"File exists: {path}. Use overwrite=True.")
        with open(p, "w", encoding="utf-8") as f:
            f.write(contents)

    # ---------- Content ----------
    def head(self, path: str | os.PathLike[str], max_bytes: int = 65536) -> str:
        p = _resolve_path(path)
        with open(p, "rb") as f:
            data = f.read(max_bytes)
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            # Best-effort for binary files
            return data.decode("utf-8", errors="replace")

    def tail(self, path: str | os.PathLike[str], max_bytes: int = 65536) -> str:
        p = _resolve_path(path)
        size = p.stat().st_size
        with open(p, "rb") as f:
            if size <= max_bytes:
                data = f.read()
            else:
                f.seek(size - max_bytes)
                data = f.read()
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("utf-8", errors="replace")

    # ---------- Introspection ----------
    def help(self) -> str:
        text = (
            "dbutils.fs commands:\n"
            "- ls(path) -> List[FileInfo]\n"
            "- mkdirs(path) -> bool\n"
            "- rm(path, recurse=False) -> bool\n"
            "- cp(src, dst, recurse=False) -> bool\n"
            "- mv(src, dst, recurse=False) -> bool\n"
            "- put(path, contents, overwrite=False) -> None\n"
            "- head(path, max_bytes=65536) -> str\n"
            "- tail(path, max_bytes=65536) -> str\n"
            "\nPaths may use dbfs:/, file:/, or local paths."
        )
        return text

    # ---------- Helpers ----------
    @staticmethod
    def _to_scheme_path(p: Path) -> str:
        try:
            root = _dbfs_root()
        except Exception:
            return str(p)
        try:
            rel = p.resolve().relative_to(root)
            return f"dbfs:/{rel.as_posix()}"
        except ValueError:
            return str(p)

