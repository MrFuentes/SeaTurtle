#!/usr/bin/env python3

import os
import subprocess
import sys
from getpass import getpass


class MyShell():

    def __init__(self):

        host = os.uname()[1]
        user = os.environ['USER']
        cwd = os.environ['PWD']
        # makes $SHELL point to myshell.py
        os.environ['SHELL'] = os.getcwd()+'/MyShell'
        env_len = len(os.environ['HOME'])
        if os.environ['HOME'] in os.getcwd():
            self.prompt = f"{user}@{host} ~{cwd[env_len:]}$ "
        else:
            # if not in /Home/user/
            self.prompt = f"{user}@{host} {cwd}$ "
        # set of functions that can be called from the command line
        self.dispatcher = {
                           'dir': self.do_dir,
                           'echo': self.do_echo,
                           'quit': self.do_quit,
                           'cd': self.do_cd,
                           'environ': self.do_env,
                           'clr': self.do_clr,
                           'pause': self.do_pause,
                           'help': self.do_help,
                          }
        # set of functions specific to batch files
        self.disbatcher = {
                           'dir': self.b_dir,
                           'echo': self.b_echo,
                           'quit': self.do_quit,
                           'cd': self.b_cd,
                           'environ': self.b_env,
                          }

    def pre(self):
        # Prints the help prompt when the shell is first opened
        print('type "help" for a list of commands')
        self.line()

    def line(self):

        ''' Main loop of the shell program '''

        # Takes user input as a list of arguments
        args = input(self.prompt).split(" ")
        invalid = f'Error: "{args[0]}" is not a valid command'
        try:
            # If the command is a shell command
            self.dispatcher[args[0]](args[1:])
            self.line()
        except KeyError:
            # If the command is not a shell command
            try:
                # If forking to background
                if args[-1] == '&':
                    for i in range(1, len(args[:-1])):
                        # If forking and overwriting
                        if args[i] == '>':
                            try:
                                self.overwrite(
                                    args[i+1],
                                    subprocess.Popen(args[:i])
                                )
                                self.line()
                            except IndexError:
                                # If no filename is provided
                                print('Error: No filename given')
                                self.line()
                            except FileNotFoundError:
                                # If the command is invalid
                                print(invalid)
                                self.line()
                        # If forking and using append
                        elif args[i] == '>>':
                            try:
                                self.append(
                                            args[i+1],
                                            subprocess.Popen(args[:i])
                                           )
                                self.line()
                            except IndexError:
                                # If no filename is given
                                print('Error: No filename given')
                                self.line()
                            except FileNotFoundError:
                                # I fthe command is invalid
                                print(invalid)
                                self.line()
                        else:
                            try:
                                # If not using IO redirection
                                subprocess.Popen(args[:-1])
                                self.line()
                            except FileNotFoundError:
                                # If the command is invalid
                                print(invalid)
                                self.line()
                else:
                    # If not forking to background
                    try:
                        subprocess.run(args)
                        self.line()
                    except FileNotFoundError:
                        # If the command is invalid
                        print(invalid)
                        self.line()
            except PermissionError:
                self.line()

    def do_help(self, args):

        ''' prints a helpstring for any of the built in commands '''

        h_dir = "\
lists the contents of the given directory \
or the current directory if none is given"
        h_echo = "\
returns a concatenated string of the arguments given"
        h_quit = "quits the shell"
        h_cd = "\
changes the current directory or \
prints the current directory if none is given"
        h_environ = "\
Prints all the environment variables \
and their corresponding values"
        h_clr = "clears the terminal"
        h_pause = "pauses the shell until the enter key is pressed"
        h_help = "\
lists the built in commands or if \
given a specific command, gives the usage of that command"
        help_list = {
                     'dir': h_dir,
                     'echo': h_echo,
                     'quit': h_quit,
                     'cd': h_cd,
                     'environ': h_environ,
                     'clr': h_clr,
                     'pause': h_pause,
                     'help': h_help
                    }
        try:
            # When using help followed by a command
            print(f'{help_list[args[0]]}')
            self.line()
        except IndexError:
            # When help is typed with no arguments
            print('Type "help" followed by one of the \
following commands for more information')
            print('='*len("   ".join(a for a in help_list)))
            print(f"{'   '.join([a for a in help_list])}")
            self.line()
        except KeyError:
            # If the command is not a built in command
            print('\
Type "help" followed by one of the \
following commands for more information')
            print('='*len("   ".join(a for a in help_list)))
            print(f"{'   '.join([a for a in help_list])}")
            self.line()

    def do_pause(self, args):

        # Pauses the shell until enter is pressed
        getpass(prompt='press "Enter" to resume shell function')
        self.line()

    def do_clr(self, args):

        # Clears the terminal and returns the prompt
        # to the top of the terminal
        sys.stdout.write('\033[2J\033[H')
        self.line()

    def do_env(self, args):

        try:
            if args[0] == '>':
                try:
                    data = os.environ
                    self.overwrite(args[1], data)
                    self.line()
                except IndexError:
                    print('Error: No filename given')
                    self.line()
            elif args[0] == '>>':
                try:
                    data = os.environ
                    self.append(args[1], data)
                    self.line()
                except IndexError:
                    print('Error: No filename given')
                    self.line()
        except IndexError:
            data = os.environ
            for a in data:
                print(f"{a}:{data[a]}")
            self.line()

    def do_cd(self, args):

        try:
            os.chdir(args[0])
            os.environ['PWD'] = os.getcwd()
            curr_dir = os.getcwd()
            if os.environ['HOME'] in curr_dir:
                curr_dir = '~' + curr_dir[len(os.environ['HOME']):]
            user = os.environ['USER']
            host = os.uname()[1]
            self.prompt = f"{user}@{host} {curr_dir}$ "
            self.line()
        except FileNotFoundError:
            print("Error: no such directory")
            self.line()
        except IndexError:
            print(os.getcwd())
            self.line()

    def do_quit(self, args):

        exit()

    def do_echo(self, args):

        comment = []
        for i in range(0, len(args)):
            if args[i] == '>':
                try:
                    self.overwrite(args[i+1], [" ".join(comment)])
                    self.line()
                except IndexError:
                    print('Error: no filename given')
                    self.line()
            elif args[i] == '>>':
                try:
                    self.append(args[i+1], [' '.join(comment)])
                    self.line()
                except IndexError:
                    print('Error: no filename given')
                    self.line()
            else:
                comment.append(args[i])
        print(' '.join(comment))
        self.line()

    def do_dir(self, args):

        try:
            if args[0] == '<':
                try:
                    data = os.listdir(self.from_file(args[1]))
                    data = '  '.join(data)
                    try:
                        if args[2] == '>':
                            try:
                                self.overwrite(args[3], data)
                                self.line()
                            except IndexError:
                                print("Error: No filename given")
                                self.line()
                        elif args[2] == '>>':
                            try:
                                self.append(args[3], data)
                                self.line()
                            except IndexError:
                                print("Error: No filename given")
                                self.line()
                        else:
                            print(data)
                            self.line()
                    except IndexError:
                        print(data)
                        self.line()
                except FileNotFoundError:
                    print(f"Error: '{args[1]}' no such file")
                    self.line()
                except IndexError:
                    print("Error: No file given")
                    self.line()
            elif args[0] == '>':
                data = os.listdir(self.cwd)
                data = '    '.join(data)
                try:
                    self.overwrite(args[1], data)
                    self.line()
                except IndexError:
                    print("Error: No filename given")
                    self.line()
            elif args[0] == '>>':
                data = os.listdir(self.cwd)
                data = '    '.join(data)
                try:
                    self.append(args[1], data)
                    self.line()
                except IndexError:
                    print("Error: No filename given")
            elif args[1] == '>':
                try:
                    data = os.listdir(args[0])
                    data = '    '.join(data)
                    try:
                        self.overwrite(args[2], data)
                        self.line()
                    except IndexError:
                        print('Error: No filename given')
                except FileNotFoundError:
                    print(f"Error: '{args[0]}' no such directory")
                    self.line()
            elif args[1] == '>>':
                try:
                    data = os.list(args[0])
                    data = '    '.join(data)
                    try:
                        self.append(args[2], data)
                        self.line()
                    except IndexError:
                        print("Error: No filename given")
                        self.line()
                except FileNotFoundError:
                    print(f"Error: '{args[0]}' no such directory")
                    self.line()
            else:
                try:
                    data = os.listdir(args[0])
                    data = '    '.join(data)
                    print(data)
                    self.line()
                except FileNotFoundError:
                    print(f"Error: '{args[0]}' no such directory")
                    self.line()
        except IndexError:
            try:
                data = os.listdir(args[0])
                data = '    '.join(data)
                print(data)
                self.line()
            except IndexError:
                data = os.listdir(os.getcwd())
                print('    '.join(data))
                self.line()

    def from_file(self, filename):

        with open(filename, 'r') as f:
            return [args.strip() for args in f.readlines()]

    def overwrite(self, filename, data):

        with open(filename, 'w+') as f:
            for a in data:
                f.write(a + '\n')

    def append(self, filename, data):
        with open(filename, 'a+') as f:
            for a in data:
                f.write(a + '\n')

    def batch(self, args):
        for command in args:
            command = command.split()
            try:
                self.disbatcher[command[0]](command[1:])
            except KeyError:
                try:
                    if args[-1] == '&':
                        for i in range(1, len(args[:-1])):
                            if args[i] == '>':
                                try:
                                    self.overwrite(
                                              args[i+1],
                                              subprocess.Popen(args[:i])
                                             )
                                except IndexError:
                                    print("Error: No filename given")
                                except FileNotFoundError:
                                    print('Error: No such file')
                            elif args[i] == '>>':
                                try:
                                    self.append(
                                           args[i+1],
                                           subprocess.Popen(args[:i])
                                          )
                                except IndexError:
                                    print("Error: No filename given")
                                except FileNotFoundError:
                                    print('Error: No such file')
                            else:
                                try:
                                    subprocess.Popen(args[:-1])
                                except FileNotFoundError:
                                    print('Error: No such file')
                    else:
                        try:
                            subprocess.run(args)
                        except FileNotFoundError:
                            print('Error: No such file')
                except PermissionError:
                    pass

    def b_dir(self, args):
        try:
            if args[0] == '<':
                try:
                    data = self.from_file(args[1])
                    data = "   ".join(os.listdir(data))
                    if args[2] == '>>':
                        try:
                            self.append(args[3], [data])
                        except IndexError:
                            print("Error: No filename given")
                    elif args[2] == '>':
                        try:
                            self.overwrite(args[3], [data])
                        except IndexError:
                            print("Error: No filename given")
                except FileNotFoundError:
                    print("Error: No such file")
            elif args[0] == '>':
                try:
                    data = "   ".join(os.listdir(os.getcwd()))
                    self.overwrite(args[1], [data])
                except IndexError:
                    print("Error: No filename given")
            elif args[0] == '>>':
                try:
                    data = '   '.join(os.listdir(os.getcwd()))
                    self.append(args[1], [data])
                except IndexError:
                    print("Error: No filename given")
            elif args[1] == '>':
                try:
                    data = '   '.join(os.listdir(args[0]))
                    self.overwrite(args[2], [data])
                except FileNotFoundError:
                    print("Error: No such directory")
                except IndexError:
                    print("Error: No filename given")
            elif args[1] == '>>':
                try:
                    data = '   '.join(os.listdir(args[0]))
                    self.append(args[2], [data])
                except FileNotFoundError:
                    print("Error: No such directory")
                except IndexError:
                    print("Error: No filename given")
            else:
                data = '   '.join(os.listdir(args[1]))
                print(data)
        except IndexError:
            try:
                data = '   '.join(os.listdir(args[1]))
                print(data)
            except IndexError:
                data = '   '.join(os.listdir(os.getcwd()))
                print(data)

    def b_echo(self, args):
        comment = []
        for i in range(1, len(args)):
            if args[i] == '>':
                try:
                    comment = " ".join(comment)
                    self.overwrite(args[i+1], comment)
                    return
                except IndexError:
                    print("Error: No filename given")
                    return
            elif args[i] == '>>':
                try:
                    comment = " ".join(comment)
                    self.append(args[i+1], comment)
                    return
                except IndexError:
                    print("Error: No filename given")
                    return
            else:
                comment.append(args[i])
        comment = " ".join(comment)
        print(comment)

    def b_cd(self, args):
        try:
            os.chdir(args[0])
            os.environ['PWD'] = os.getcwd()
            curr_dir = os.getcwd()
            if os.environ['HOME'] in curr_dir:
                curr_dir = '~' + curr_dir[len(os.environ['HOME']):]
            user = os.environ['USER']
            host = os.uname()[1]
            self.prompt = f"{user}@{host} {curr_dir}$ "
        except FileNotFoundError:
            print("Error: no such directory")
        except IndexError:
            print(os.getcwd())

    def b_quit(self, args):
        exit()

    def b_env(self, args):

        try:
            if args[0] == '>':
                try:
                    data = os.environ
                    data_list = []
                    for a in data:
                        data_list.append(f"{a}:{data[a]}")
                    self.overwrite(args[1], data_list)
                except IndexError:
                    print('Error: No filename given')
            elif args[0] == '>>':
                try:
                    data = os.environ
                    data_list = []
                    for a in data:
                        data_list.append(f"{a}:{data[a]}")
                    self.append(args[1], data_list)
                except IndexError:
                    print('Error: No filename given')
        except IndexError:
            data = os.environ
            for a in data:
                print(f"{a}:{data[a]}")


if __name__ == "__main__":
    try:
        with open(sys.argv[1], 'r') as f:
            commands = f.readlines()
            commands.append('quit' + '\n')
            shell = MyShell()
            shell.batch(commands)
    except FileNotFoundError:
        print('No such file')
    except IndexError:
        MyShell().pre()
