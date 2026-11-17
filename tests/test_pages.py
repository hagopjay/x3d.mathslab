"""Static-hosting contract: every module the in-browser runtime installs exists and is stdlib-only."""
import ast
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STDLIB = set(sys.stdlib_module_names)


class PagesContract(unittest.TestCase):
    def modules(self):
        text = (ROOT / 'web/static-api.js').read_text(encoding='utf-8')
        match = re.search(r'const MODULES = \[([^\]]+)\]', text)
        self.assertIsNotNone(match)
        return re.findall(r'"(\w+)"', match.group(1))

    def test_every_installed_module_exists(self):
        for name in self.modules():
            self.assertTrue((ROOT / 'mathlab' / f'{name}.py').is_file(), name)

    def test_installed_modules_import_only_stdlib_and_each_other(self):
        installed = set(self.modules())
        for name in installed:
            tree = ast.parse((ROOT / 'mathlab' / f'{name}.py').read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots = [a.name.split('.')[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    roots = [(node.module or '').split('.')[0]]
                else:
                    continue
                for root in roots:
                    self.assertIn(root, STDLIB, f'{name} imports non-stdlib {root}')

    def test_installed_set_covers_server_dependencies(self):
        for name in self.modules():
            tree = ast.parse((ROOT / 'mathlab' / f'{name}.py').read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module:
                    self.assertIn(node.module.split('.')[0], self.modules(), f'{name} -> .{node.module}')

    def test_manim_is_never_installed_in_the_browser(self):
        self.assertNotIn('mcp_server', self.modules())
        text = (ROOT / 'web/static-api.js').read_text(encoding='utf-8')
        self.assertNotIn('import manim', text)


if __name__ == '__main__':
    unittest.main()
