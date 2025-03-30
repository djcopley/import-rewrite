from __future__ import annotations

import ast
import importlib.abc
import importlib.machinery
import importlib.util
import logging
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import types
    from collections.abc import Sequence


class ImportTransformer(ast.NodeTransformer):
    def __init__(self, import_map: dict[str, str] | None = None) -> None:
        self.import_map = import_map or {}
        self.modified = False

    def visit_Import(self, node: ast.Import) -> ast.AST:  # noqa: N802
        new_names = []
        for name in node.names:
            if name.name in self.import_map:
                self.modified = True
                new_name = self.import_map[name.name]
                new_names.append(ast.alias(name=new_name, asname=name.asname or name.name))
                logging.getLogger(__name__).debug("Rewriting import: %s → %s", name.name, new_name)
            else:
                new_names.append(name)

        node.names = new_names
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:  # noqa: N802
        if node.module in self.import_map:
            self.modified = True
            new_module = self.import_map[node.module]
            logging.getLogger(__name__).debug("Rewriting from import: %s → %s", node.module, new_module)
            node.module = new_module

        return node


class ImportRewritingFinder(importlib.abc.MetaPathFinder):
    def __init__(self, import_map: dict[str, str] | None = None) -> None:
        self.import_map = import_map or {}

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str | bytes] | None,
        target: types.ModuleType | None = None,  # noqa: ARG002
    ) -> importlib.machinery.ModuleSpec | None:
        if path is None:
            path = sys.path

        for entry in path:
            if not isinstance(entry, str) or not os.path.isdir(entry):
                continue

            for suffix in importlib.machinery.SOURCE_SUFFIXES:
                filename = os.path.join(entry, fullname.split(".")[-1] + suffix)
                if not os.path.exists(filename):
                    continue

                loader = ImportRewritingLoader(fullname, filename, self.import_map)

                return importlib.machinery.ModuleSpec(name=fullname, loader=loader, origin=filename, is_package=False)

        return None


class ImportRewritingLoader(importlib.abc.SourceLoader):
    def __init__(self, fullname: str, path: str, import_map: dict[str, str] | None = None):
        self.fullname = fullname
        self.path = path
        self.import_map = import_map or {}

    def get_filename(self, fullname: str) -> str:  # noqa: ARG002
        return self.path

    def get_data(self, path: str | bytes) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def exec_module(self, module: types.ModuleType) -> None:
        source_bytes = self.get_data(self.get_filename(self.fullname))
        source = source_bytes.decode("utf-8")

        tree = ast.parse(source)
        transformer = ImportTransformer(self.import_map)
        transformed_tree = transformer.visit(tree)

        if transformer.modified:
            ast.fix_missing_locations(transformed_tree)
            code = compile(transformed_tree, self.get_filename(self.fullname), "exec")
            exec(code, module.__dict__)  # noqa: S102
        else:
            code = compile(source, self.get_filename(self.fullname), "exec")
            exec(code, module.__dict__)  # noqa: S102


def install_import_rewriter(
    import_map: dict[str, str] | None = None,
) -> ImportRewritingFinder:
    """Install the import rewriting hook with the specified mapping.

    :param import_map: A dictionary mapping original import names to replacement names.
                       For example: {'requests': 'my_requests'}
    :returns: The finder instance that was installed.
    """
    import_map = import_map or {}
    finder = ImportRewritingFinder(import_map)
    sys.meta_path.insert(0, finder)
    return finder
