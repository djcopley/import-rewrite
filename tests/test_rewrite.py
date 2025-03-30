import importlib
import sys

from import_rewriter import install_import_rewriter


def test_direct_import_rewriting():
    """Test rewriting of direct imports (import x)."""
    install_import_rewriter({"original_module": "replacement_module"})
    import test_module_direct

    assert test_module_direct.get_value() == "replacement"


def test_from_import_rewriting():
    """Test rewriting of from imports (from x import y)."""
    install_import_rewriter({"original_module": "replacement_module"})
    import test_module_from

    assert test_module_from.get_value() == "replacement"


def test_unaffected_imports():
    """Test that imports not in the mapping are unaffected."""
    install_import_rewriter({"some_other_module": "replacement_module"})
    import unaffected_module

    assert unaffected_module.test_function() == "unaffected"


def test_multiple_imports():
    """Test a module with multiple imports where only some should be rewritten."""
    install_import_rewriter({"original_module": "replacement_module", "third_module": "replacement_third"})
    import test_module_multiple

    assert test_module_multiple.get_value() == "replacement"


def test_install_uninstall():
    """Test installing and uninstalling the rewriter."""
    finder = install_import_rewriter({"original_module": "replacement_module"})
    import test_module_direct

    assert test_module_direct.get_value() == "replacement"
    sys.meta_path.remove(finder)
    importlib.reload(test_module_direct)
    assert test_module_direct.get_value() == "original"


def test_reloader_functionality():
    """Test that reloading a module applies the new import rewrites."""
    import test_module_direct

    assert test_module_direct.get_value() == "original"
    install_import_rewriter({"original_module": "replacement_module"})
    importlib.reload(test_module_direct)
    importlib.reload(test_module_direct)  # test multiple reloads
    assert test_module_direct.get_value() == "replacement"
