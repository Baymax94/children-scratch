import os
import sys
import zmq
import subprocess
import pathlib
import platform

from codelab_adapter import settings
from codelab_adapter.core_extension import Extension
from codelab_adapter.utils import ui_info


def which(program):
    """Determines whether program exists
    """

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file


def get_python_path():
    # If it is not working,  Please replace python3_path with your local python3 path. shell: which python3
    path = 'python'
    if platform.system() == "Darwin":
        path = "/usr/local/bin/python3"
    if platform.system() == "Windows":
        path = "python"
    if platform.system() == "Linux":
        path = "/usr/bin/python3"
    return path


def run_pando_server():
    python_path = get_python_path()
    codelab_adapter_server_dir = pathlib.Path.home(
    ) / "codelab_adapter" / "servers"
    script = "{}/pando_server.py".format(codelab_adapter_server_dir)
    shell_cmd = [python_path, script]
    pando_server = subprocess.Popen(shell_cmd)
    settings.running_child_procs.append(pando_server)


class PandoExtension(Extension):
    def __init__(self):
        name = type(self).__name__
        super().__init__(name)
        self.prefix = 'pando'

    def run(self):

        run_pando_server()

        # zmq socket
        port = 38789
        context = zmq.Context.instance()
        client = context.socket(zmq.REQ)
        client.connect("tcp://localhost:%s" % port)
        while True:
            message = self.read()
            payload = message.get("payload")
            if self.prefix in payload:
                self.logger.debug("payload: {}".format(payload))
                client.send_json({"action": payload})
                result = client.recv_json().get("result")


export = PandoExtension


