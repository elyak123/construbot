import subprocess, shlex
from pathlib import Path
import os, sys, site

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

def get_windows_script_location():
    packages = site.getsitepackages()
    for folder in packages:
        folder = os.path.join(folder, 'Scripts')
        command = subprocess.run(['dir', '\ad', folder], shell=True, stdout=subprocess.PIPE)
        folder_contents = str(command.stdout.decode('utf-8', errors='ignore').encode('utf-8'))
        if command.returncode != 0 and 'mkvirtualenv.bat' in folder_contents.stdout.decode().split('\n'):
            return folder
    raise FileNotFoundError('El script no se encuentra, virtualenvwrapper esta instalado?')

def run_bash_function(library_path, function_name, params):
    params = shlex.split('"source %s; %s %s"' % (library_path, function_name, params))
    cmdline = ['bash', '-c'] + params
    process = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError("'%s' failed, error code: '%s', stdout: '%s', stderr: '%s'" % (
            ' '.join(cmdline), process.returncode, stdout.rstrip(), stderr.rstrip()))
    return print(stdout.strip())

def make_virtual_env(script_location=SCRIPT_LOCATION, name=VIRTUAL_ENV_NAME):
    if get_platform() == 'unix':
        run_bash_function(script_location, 'mkvirtualenv', name)
    else:
        script_location = get_windows_script_location()
        # for location in site.getsitepackages():
        #     try:
        #         script = location + 'Scripts/mkvirtualenv.bat/'
        #         subprocess.run([script])
        #         break
        #     except FileNotFoundError:
        #         continue
        # raise FileNotFoundError
        #
        # script_location = VIRTUAL_ENV_FOLDER + 'Scripts/mkvirtualenv.bat'
        subprocess.run([script_location])

def configure_virtual_env(postactive_location=POSTACTIVE_LOCATION, name=VIRTUAL_ENV_NAME):
    if get_platform() == 'unix':
        with open(postactive_location, 'w', newline='\n') as file:
            file.write('{0}_root={1}\ncd ${0}_root\nPATH=${0}_root/bin:$PATH'.format(name, cwd))

def update_virtual_env(venv_folder=VIRTUAL_ENV_FOLDER):
    if get_platform() == 'unix':
        pip_location = venv_folder + 'bin/pip'
    else:
        pip_location = venv_folder + 'Scripts/pip'
    subprocess.run([pip_location, 'install', '-r', 'requirements.txt'])

def main(venv_name=VIRTUAL_ENV_NAME, venv_wrapper=SCRIPT_LOCATION, postactive_location=POSTACTIVE_LOCATION):
    install_virtualenvwrapper()
    make_virtual_env()
    configure_virtual_env()
    update_virtual_env()


if __name__ == '__main__':
    main()
