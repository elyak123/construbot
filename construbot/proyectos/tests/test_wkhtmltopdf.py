import subprocess
from test_plus.test import TestCase


class TestwkhtmltopdfBinary(TestCase):

    def test_wkhtmltopdf_binary_works(self):
        command = subprocess.run(['wkhtmltopdf', '--help', '>', '/dev/null'], stdout=subprocess.DEVNULL)
        self.assertEqual(command.returncode, 0)
