import subprocess, shlex
from pathlib import Path
import os

home = home = str(Path.home())
VIRTUAL_ENV_NAME = 'construbot'
VIRTUAL_ENV_FOLDER = home + '/.virtualenvs/{}/'.format(VIRTUAL_ENV_NAME)
POSTACTIVE_LOCATION = VIRTUAL_ENV_FOLDER + 'bin/postactivate'
SCRIPT_LOCATION = '/usr/local/bin/virtualenvwrapper.sh'
ACTIVATE = home + VIRTUAL_ENV_FOLDER + 'bin/activate'
cwd = os.getcwd()

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
    run_bash_function(script_location, 'mkvirtualenv', name)

def configure_virtual_env(postactive_location=POSTACTIVE_LOCATION, name=VIRTUAL_ENV_NAME):
    with open(postactive_location, 'w', newline='\n') as file:
        file.write('{0}_root={1}\ncd ${0}_root\nPATH=${0}_root/bin:$PATH'.format(name, cwd))

def update_virtual_env(venv_folder=VIRTUAL_ENV_FOLDER):
    pip_location = venv_folder + 'bin/pip'
    subprocess.run([pip_location, 'install', '-r', 'requirements.txt'])

def main(venv_name=VIRTUAL_ENV_NAME, venv_wrapper=SCRIPT_LOCATION, postactive_location=POSTACTIVE_LOCATION):
    make_virtual_env()
    configure_virtual_env()
    update_virtual_env()


if __name__ == '__main__':
    main()
