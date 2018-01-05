import subprocess, shlex
from pathlib import Path
import os


#subprocess.run(['/usr/local/bin/virtualenvwrapper.sh && mkvirtualenv -h'], executable='bash')
#subprocess.Popen(['bash', '-c', '. /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv'])
# library_path = '/usr/local/bin/virtualenvwrapper.sh'
# function_name = 'mkvirtualenv'
# params = '-h'
# params = shlex.split('"source %s; %s %s"' % (library_path, function_name, params))
# cmdline = ['bash', '-c'] + params
# subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
home = home = str(Path.home())
VIRTUAL_ENV_NAME = 'construbot'
POSTACTIVE_LOCATION = home + '/.virtualenvs/{}/bin/postactivate'.format(VIRTUAL_ENV_NAME)
SCRIPT_LOCATION = '/usr/local/bin/virtualenvwrapper.sh'
ACTIVATE = home + '/.virtualenvs/{}/bin/activate'.format(VIRTUAL_ENV_NAME)
cwd = os.getcwd()
def run_bash_function(library_path, function_name, params):
    params = shlex.split('"source %s; %s %s"' % (library_path, function_name, params))
    cmdline = ['bash', '-c'] + params
    print(cmdline)
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

# def workon_virtualenv(script=ACTIVATE, env_name=VIRTUAL_ENV_NAME):
#     #run_bash_function(script, 'workon', env_name)
#     #command = '. ' + script + ';' + ' workon ' + env_name
#     subprocess.Popen(['bash', '-c', script], shell=True, executable='bash')
#     #params = shlex.split('"source %s; %s %s"' % (script, 'workon', env_name))
#     #cmdline = ['bash', '-c'] + params
#     #subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)


def main(venv_name=VIRTUAL_ENV_NAME, venv_wrapper=SCRIPT_LOCATION, postactive_location=POSTACTIVE_LOCATION):
    make_virtual_env()
    configure_virtual_env()
    #workon_virtualenv()


if __name__ == '__main__':
    main()
