import sublime, sublime_plugin
import os
import subprocess

def execute(args, cwd, decode=True):
    """Execute a git command synchronously and return its output.

    Arguments:
        args (list): The command line arguments used to run git.
        decode (bool): If True the git's output is decoded assuming utf-8
                  which is the default output encoding of git.

    Returns:
        string: The decoded or undecoded output read from stdout.
        string: an error message if something went wrong
    """
    stdout, stderr = None, None

    try:
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(
            args=args, cwd=cwd, startupinfo=startupinfo,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.PIPE)
        stdout, stderr = proc.communicate()
    except OSError as error:
        # Print out system error message in debug mode.
       return (None, error)
    # return decoded ouptut using utf-8 or binary output
    return (stdout.decode('utf-8').strip() if decode else stdout, stderr.decode('utf-8').strip())

EDITING_PATH = "/home/jspear/Documents/SublimeGitMemory/"

# Run ./run.py whenever a change is made in the editing path
'''
class HotReloader(sublime_plugin.EventListener):

    def on_modified(self, view):
        file_name = view.file_name()
        if file_name:
            is_subpath = file_name.startswith(EDITING_PATH)
            if is_subpath:
                execute(['./run.py'], EDITING_PATH)


'''
