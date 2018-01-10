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

from pathlib import Path
import subprocess
import shlex
import os
import sys
import site

home = str(Path.home())
VIRTUAL_ENV_NAME = 'construbot'
VIRTUAL_ENV_FOLDER = home + '/.virtualenvs/{}/'.format(VIRTUAL_ENV_NAME)
POSTACTIVE_LOCATION = VIRTUAL_ENV_FOLDER + 'bin/postactivate'
SCRIPT_LOCATION = '/usr/local/bin/virtualenvwrapper.sh'
ACTIVATE = home + VIRTUAL_ENV_FOLDER + 'bin/activate'
cwd = os.getcwd()


def get_platform():
    windows = ['win32', 'cygwin']
    platform = 'unix' if sys.platform not in windows else 'windows'
    return platform


def install_virtualenvwrapper(venv_folder=VIRTUAL_ENV_FOLDER):
    platform = get_platform()
    if platform == 'unix':
        package = 'virtualenvwrapper'
    else:
        package = 'virtualenvwrapper-win'
    subprocess.run(['pip3', 'install', package])
    return package


def get_site_packages():
    packages = site.getsitepackages()
    return packages


def get_windows_script_location(target_script):
    packages = get_site_packages()
    for folder in packages:
        folder = os.path.join(folder, 'Scripts')
        command = subprocess.run(['dir', '\ad', folder], shell=True, stdout=subprocess.PIPE)
        folder_contents = str(command.stdout.decode('utf-8', errors='ignore').encode('utf-8'))
        if command.returncode == 0 and target_script in folder_contents:
            file_name = folder + '\\' + target_script
            return file_name
    raise FileNotFoundError('El script no se encuentra, virtualenvwrapper esta instalado?')


def run_bash_function(library_path, function_name, params):
    params = shlex.split('"source %s; %s %s"' % (library_path, function_name, params))
    cmdline = ['bash', '-c'] + params
    process = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError("'%s' failed, error code: '%s', stdout: '%s', stderr: '%s'" % (
            ' '.join(cmdline), process.returncode, stdout.rstrip(), stderr.rstrip()))
    return stdout.strip()


def make_virtual_env(script_location=SCRIPT_LOCATION, name=VIRTUAL_ENV_NAME):
    if get_platform() == 'unix':
        run_bash_function(script_location, 'mkvirtualenv', name)
    else:
        script_location = get_windows_script_location('mkvirtualenv.bat')
        command = script_location + ' construbot'
        proceso = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proceso.returncode != 0:
            raise RuntimeError("'%s' failed, error code: '%s'" % (
                ' '.join(script_location), proceso.returncode))


def configure_virtual_env(postactive_location=POSTACTIVE_LOCATION, name=VIRTUAL_ENV_NAME):
    if get_platform() == 'unix':
        with open(postactive_location, 'w', newline='\n') as file:
            file.write('{0}_root={1}\ncd ${0}_root\nPATH=${0}_root/bin:$PATH'.format(name, cwd))


def update_virtual_env(venv_folder=VIRTUAL_ENV_FOLDER):
    if get_platform() == 'unix':
        pip_location = venv_folder + 'bin/pip'
        coverage_location = venv_folder + 'bin/coverage'
    else:
        pip_location = venv_folder + '\Scripts\pip'
        coverage_location = venv_folder + '\Scripts\coverage'
    subprocess.run([pip_location, 'install', '-r', 'requirements.txt'])
    # Tenemos que checar si los binarios tambien se instalaron correctamente...
    bin_test = subprocess.run(
        [coverage_location, '-h'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    if bin_test.returncode != 0:
        # Si no... hay que reinstalar todas las dependencias... issue #1
        raise RuntimeError(
            'Dependencies installed correctly, however binaries didn\'t. Please run:\n'
            'pip uninstall -r requirements.txt -y && pip install -r requirements.txt\n'
            'from inside the virtual environment')


def main(venv_name=VIRTUAL_ENV_NAME, venv_wrapper=SCRIPT_LOCATION, postactive_location=POSTACTIVE_LOCATION):
    install_virtualenvwrapper()
    make_virtual_env()
    configure_virtual_env()
    if get_platform() == 'unix':
        update_virtual_env()
    else:
        pip_location = home + '\\' + 'Envs\\' + venv_name
        update_virtual_env(venv_folder=pip_location)


if __name__ == '__main__':
    main()
