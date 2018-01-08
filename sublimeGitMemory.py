'''import sublime, sublime_plugin
import os
import subprocess
from functools import partial
import threading
import time

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

def get_branch_name(file_name):
    # This doesn't work when head is detached. Ignore this case for now.
    path, name = os.path.split(file_name)
    output, err = execute(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], path)
    if err:
        print(err)
        return
    return output

def get_git_path(file_name):
    path, name = os.path.split(file_name)
    output, err = execute(['git', 'rev-parse', '--show-toplevel'], path)
    if err:
        print(err)
        return
    return output

def in_git_tree(file_name):
    path, name = os.path.split(file_name)
    output, err = execute(['git', 'rev-parse', '--show-toplevel'], path)
    return not err

memory = {}

def get_specifier(file_name):
    if in_git_tree(file_name) and (file_name is not None):
        git_path = get_git_path(file_name)

        branch_name = get_branch_name(file_name)

        return (branch_name, git_path)
    return None

def add_to_memory(file_name, memory):
    specifier = get_specifier(file_name)
    if specifier is not None:
        if specifier in memory:
            if file_name not in memory[specifier]:
                memory[specifier].append(file_name)
        else:
            memory[specifier] = [file_name]

def remove_from_memory(file_name, memory):
    specifier = get_specifier(file_name)
    if specifier is not None:
        if specifier in memory:
            if file_name in memory[specifier]:
                memory[specifier].remove(file_name)

# Assume we have 1 window, and all files are in the same git repo
# When I switch to a new branch, close all files assosciated with old branch, and open all files assosciated with new branch.

class EventDump(sublime_plugin.EventListener):
    def on_load(self, view):
        file_name = view.file_name()
        add_to_memory(file_name, memory)
        print('Memory: ' + str(memory))

    def on_activated(self, view):
        active_view = view

    def on_post_save(self, view):
        file_name = view.file_name()
        add_to_memory(file_name, memory)
        print('Memory: ' + str(memory))

    def on_pre_close(self, view):
        file_name = view.file_name()
        remove_from_memory(file_name, memory)

current_specifier = None
active_view = sublime.active_window().active_view()

def set_current_specifier():
    current_specifier = get_specifier(active_view.file_name())
    print(current_specifier)

class GitChecker(threading.Thread):
    def __init__(self):
        self.result = None
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while True:
            i = 0
            if not self._stop_event.isSet():
                global current_specifier
                current_specifier = get_specifier(active_view.file_name())
                print('Specifier: ' + str(current_specifier) + ' at t-' + str(i))
                result = current_specifier
                time.sleep(1)
                i = i + 1

thread = None

class KillCommand(sublime_plugin.TextCommand):
    def run(self, view):
        global thread
        print('Killed: ' + str(thread))
        thread.stop()

class StartCommand(sublime_plugin.TextCommand):
    def run(self, view):
        global thread
        thread = GitChecker()
        thread.start()


'''
