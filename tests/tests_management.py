import sys
from unittest import mock
from django.test  import TestCase
from scripts import devinstall


class ManagementFunctionsTest(TestCase):

    @mock.patch('sys.platform', 'win32')
    def test_platform_returns_correct_variable_for_windows(self):
        platform = devinstall.get_platform()
        self.assertEqual(platform, 'windows')

    @mock.patch('sys.platform', 'darwin')
    def test_platform_returns_correct_variable_for_mac(self):
        platform = devinstall.get_platform()
        self.assertEqual(platform, 'unix')

    @mock.patch('sys.platform', 'linux')
    def test_platform_returns_correct_variable_for_linux(self):
        platform = devinstall.get_platform()
        self.assertEqual(platform, 'unix')

    @mock.patch('sys.platform', 'linux')
    def test_installs_correct_virtualenvwrapper(self):
        with mock.patch('subprocess.run') as run_mock:
            process = devinstall.install_virtualenvwrapper()
            self.assertEqual(process, 'virtualenvwrapper')

    @mock.patch('sys.platform', 'darwin')
    def test_installs_correct_virtualenvwrapper_for_mac(self):
        with mock.patch('subprocess.run') as run_mock:
            process = devinstall.install_virtualenvwrapper()
            self.assertEqual(process, 'virtualenvwrapper')

    @mock.patch('sys.platform', 'win32')
    def test_installs_correct_virtualenvwrapper_for_windows(self):
        with mock.patch('subprocess.run') as run_mock:
            process = devinstall.install_virtualenvwrapper()
            self.assertEqual(process, 'virtualenvwrapper-win')