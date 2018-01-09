"""
    Copyright (C) 2018  Javier Llamas Ramirez

    email elyak.123@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import subprocess
import site
from unittest import mock
from django.test import TestCase
from scripts import devinstall


class OSVariableTest(TestCase):

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


class VirtualenvWapperInstall(TestCase):
    @mock.patch('sys.platform', 'linux')
    def test_installs_correct_virtualenvwrapper(self):
        with mock.patch('subprocess.run') as run_mock:
            mocked = mock.Mock()
            attrs = {'communicate.return_value': ('output', 'error')}
            mocked.configure_mock(**attrs)
            run_mock.return_value = mocked
            process = devinstall.install_virtualenvwrapper()
            self.assertTrue(run_mock.called)
            run_mock.assert_called_with(['pip3', 'install', 'virtualenvwrapper'])
            self.assertEqual(process, 'virtualenvwrapper')

    @mock.patch('sys.platform', 'darwin')
    def test_installs_correct_virtualenvwrapper_for_mac(self):
        with mock.patch('subprocess.run') as run_mock:
            mocked = mock.Mock()
            attrs = {'communicate.return_value': ('output', 'error')}
            mocked.configure_mock(**attrs)
            run_mock.return_value = mocked
            process = devinstall.install_virtualenvwrapper()
            self.assertTrue(run_mock.called)
            run_mock.assert_called_with(['pip3', 'install', 'virtualenvwrapper'])
            self.assertEqual(process, 'virtualenvwrapper')

    @mock.patch('sys.platform', 'win32')
    def test_installs_correct_virtualenvwrapper_for_windows(self):
        with mock.patch('subprocess.run') as run_mock:
            mocked = mock.Mock()
            attrs = {'communicate.return_value': ('output', 'error')}
            mocked.configure_mock(**attrs)
            run_mock.return_value = mocked
            process = devinstall.install_virtualenvwrapper()
            self.assertTrue(run_mock.called)
            run_mock.assert_called_with(['pip3', 'install', 'virtualenvwrapper-win'])
            self.assertEqual(process, 'virtualenvwrapper-win')


class MakeVirtualEnv(TestCase):

    @mock.patch('sys.platform', 'darwin')
    def test_run_bash_function_success(self):
        with mock.patch('subprocess.Popen') as run_mock:
            mocked = mock.Mock()
            attrs = {
                'communicate.return_value': ('output', 'error'),
                'returncode': 0
            }
            mocked.configure_mock(**attrs)
            run_mock.return_value = mocked
            devinstall.make_virtual_env()
            run_mock.assert_called_with([
                'bash', '-c', 'source /usr/local/bin/'
                'virtualenvwrapper.sh; mkvirtualenv construbot'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

    @mock.patch('sys.platform', 'darwin')
    def test_run_bash_function_err(self):
        with mock.patch('subprocess.Popen') as run_mock:
            mocked = mock.Mock()
            attrs = {
                'communicate.return_value': ('output', 'error'),
                'returncode': 1
            }
            mocked.configure_mock(**attrs)
            run_mock.return_value = mocked
            with self.assertRaises(RuntimeError):
                devinstall.make_virtual_env()
                run_mock.assert_called_with([
                    'bash', '-c', 'source /usr/local/bin/'
                    'virtualenvwrapper.sh; mkvirtualenv construbot'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )


    @mock.patch('scripts.devinstall.get_site_packages')
    def test_get_windows_script_path(self, packages_list):
        with mock.patch('subprocess.run') as run_mock:
            packages_list.return_value = ['C:\\', 'D:\\']
            mocked = mock.Mock()
            decode_mock = mock.Mock()
            folder_contents = ['mkvirtualenv', 'rmvirtualenv']
            decode_attrs = {
                'encode.return_value': folder_contents,
            }
            attrs = {
                'stdout.decode.return_value': decode_mock,
                'returncode': 0,
            }
            decode_mock.configure_mock(**decode_attrs)
            mocked.configure_mock(**attrs)
            run_mock.return_value = mocked
            devinstall.get_windows_script_location('mkvirtualenv')
            run_mock.assert_called_with(['dir', '\ad', 'C:\\/Scripts'], shell=True, stdout=subprocess.PIPE)


    @mock.patch('scripts.devinstall.get_site_packages')
    def test_get_windows_script_path_raises_error(self, packages_list):
        with mock.patch('subprocess.run') as run_mock:
            packages_list.return_value = ['C:\\', 'D:\\']
            mocked = mock.Mock()
            decode_mock = mock.Mock()
            folder_contents = ['othercommand', 'rmvirtualenv']
            decode_attrs = {
                'encode.return_value': folder_contents,
            }
            attrs = {
                'stdout.decode.return_value': decode_mock,
                'returncode': 0,
            }
            decode_mock.configure_mock(**decode_attrs)
            mocked.configure_mock(**attrs)
            run_mock.return_value = mocked
            with self.assertRaises(FileNotFoundError):
                devinstall.get_windows_script_location('mkvirtualenv')


    @mock.patch('scripts.devinstall.get_platform')
    def test_make_unix_virtual_env_success(self, mock_platform):
        with mock.patch('subprocess.Popen') as run_mock:
            mock_platform.return_value = 'unix'
            mocked = mock.Mock()
            attrs = {
                'communicate.return_value': ('output', 'error'),
                'returncode': 0,
            }
            mocked.configure_mock(**attrs)
            run_mock.return_value = mocked
            devinstall.make_virtual_env()
            self.assertTrue(run_mock.called)
            run_mock.assert_called_with(
                ['bash', '-c', 'source /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv construbot'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )

    @mock.patch('scripts.devinstall.get_platform')
    def test_make_unix_virtual_env_raises_error(self, mock_platform):
        with mock.patch('subprocess.Popen') as run_mock:
            mock_platform.return_value = 'unix'
            mocked = mock.Mock()
            attrs = {
                'communicate.return_value': ('output', 'error'),
                'returncode': 1,
            }
            mocked.configure_mock(**attrs)
            run_mock.return_value = mocked
            with self.assertRaises(RuntimeError):
                devinstall.make_virtual_env()

    @mock.patch('scripts.devinstall.get_platform')
    @mock.patch('scripts.devinstall.get_windows_script_location')
    def test_make_windows_virtual_env(self, win_script_path, mock_platform):
        with mock.patch('subprocess.run') as run_mock:
            mock_platform.return_value = 'windows'
            win_script_path.return_value = 'C:\\mkvirtualenv.bat'
            mocked = mock.Mock()
            attrs = {
                'communicate.return_value': ('output', 'error'),
                'returncode': 0,
            }
            mocked.configure_mock(**attrs)
            run_mock.return_value = mocked
            devinstall.make_virtual_env()
            run_mock.assert_called_with(
                'C:\\mkvirtualenv.bat construbot',
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )


    @mock.patch('scripts.devinstall.get_platform')
    @mock.patch('scripts.devinstall.get_windows_script_location')
    def test_make_windows_virtual_env_raises_error(self, win_script_path, mock_platform):
        with mock.patch('subprocess.run') as run_mock:
            mock_platform.return_value = 'windows'
            win_script_path.return_value = 'C:\\mkvirtualenv.bat'
            mocked = mock.Mock()
            attrs = {
                'communicate.return_value': ('output', 'error'),
                'returncode': 1,
            }
            mocked.configure_mock(**attrs)
            run_mock.return_value = mocked
            with self.assertRaises(RuntimeError):
                devinstall.make_virtual_env()


class ConfigureVirtualEnv(TestCase):

    @mock.patch('scripts.devinstall.POSTACTIVE_LOCATION', '/Users/bin/postactivate')
    @mock.patch('scripts.devinstall.cwd', '/Users/myuser')
    @mock.patch('sys.platform', 'unix')
    def test_configure_virtual_env(self):
        mopen = mock.mock_open()
        with mock.patch('__main__.open', mopen):
            import pdb; pdb.set_trace()
            devinstall.configure_virtual_env()
            #mopen.assert_called_once_with('foo', 'w')
            mopen.assert_called_with(
                 'construbot_root=/Users/myuser \ncd $construbot_root\nPATH=$construbot_root/bin:$PATH',

            )
            # handle = mopen.write.assert_called_once_with(
            #     'construbot_root=%s \ncd $construbot_root\nPATH=$construbot_root/bin:$PATH' % devinstall.cwd
            # )

