import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PythonVersionTests(unittest.TestCase):
    def test_old_interpreter_reports_actionable_error(self):
        for module in ('playbook', 'orchestration'):
            with self.subTest(module=module):
                script = "import runpy, sys; sys.version_info = (3, 6, 0); runpy.run_module(%r, run_name='__main__')" % module
                result = subprocess.run([sys.executable, '-c', script], cwd=ROOT, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Python 3.11 or newer is required', result.stderr)
                self.assertIn('python3.11 -m ' + module, result.stderr)
                self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
