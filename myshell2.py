#!/usr/bin/env python3

import os
import readline
import subprocess
import sys
import termios
import tty
from getpass import getpass

def getch():
    # Parses keypresses without having to press Enter
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch
    
# tab key calls the complete function
readline.parse_and_bind("tab: complete")
def complete(text, state):
    volcab = ['dir','echo','quit','cd','environ','clr','pause','help']
    results = [x for x in volcab if x.startswith(text)] + [None]
    # returns the completed function name
    return results[state]
readline.set_completer(complete)

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

        commands = []
        # Takes user input as a list of arguments
        args = input(self.prompt).split(" ")
        commands.append(args)
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
            if args[0] == 'more':
            # If using 'help more' command
                # Gets list of all lines from 'readme'
                lines = open('readme', 'r').readlines()
                def more(lines):
                    if len(lines) <= 20:
                        for i in range(0, len(lines)):
                            # prints the rest of the lines if there are 20 or less left
                            print(lines.pop(0).strip())
                    for i in range(0,20):
                        # pops and prints the next line from readme 20 times
                        print(lines.pop(0).strip())
                more(lines)
                while len(lines) != 0:
                    # checks keypresses until all the lines are printed
                    char = getch()
                    if char == ' ':
                        # if the spacebar is pressed, print the next block of text
                        more(lines)
                    elif char == 'q':
                        # if q is pressed, return to the prompt
                        self.line() 
                self.line()
            else:
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
following commands or "more" for more information')
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
            # if using overwrite
            if args[0] == '>':
                try:
                    data = os.environ
                    # outputs environment strings to the given file
                    self.overwrite(args[1], data)
                    self.line()
                except IndexError:
                    # if no filename is given
                    print('Error: No filename given')
                    self.line()
            # if using append
            elif args[0] == '>>':
                try:
                    data = os.environ
                    # outputs environment strings to the given file
                    self.append(args[1], data)
                    self.line()
                except IndexError:
                    # if no filename is given
                    print('Error: No filename given')
                    self.line()
        except IndexError:
            # if no output is used
            data = os.environ
            # prints environment strings to the terminal
            for a in data:
                print(f"{a}:{data[a]}")
            self.line()

    def do_cd(self, args):

        try:
            # changes directory to the given directory
            os.chdir(args[0])
            # $CWD points to current directory
            os.environ['PWD'] = os.getcwd()
            curr_dir = os.getcwd()
            # changes the promtp to the current directory
            if os.environ['HOME'] in curr_dir:
                # if $HOME in the directory, shorten to ~/
                curr_dir = '~' + curr_dir[len(os.environ['HOME']):]
            user = os.environ['USER']
            host = os.uname()[1]
            # update prompt
            self.prompt = f"{user}@{host} {curr_dir}$ "
            self.line()
        except FileNotFoundError:
            # If the directory doesn't exist
            print("Error: no such directory")
            self.line()
        except IndexError:
            # if using cd without and argument
            # prints the current directory
            print(os.getcwd())
            self.line()

    def do_quit(self, args):

        # exits the shell
        exit()

    def do_echo(self, args):

        comment = []
        for i in range(0, len(args)):
            # if using overwrite
            if args[i] == '>':
                try:
                    # outputs the comment to the given file
                    self.overwrite(args[i+1], [" ".join(comment)])
                    self.line()
                except IndexError:
                    # if no filename is given
                    print('Error: no filename given')
                    self.line()
            # if using append
            elif args[i] == '>>':
                try:
                    # outputs the comment to the given file
                    self.append(args[i+1], [' '.join(comment)])
                    self.line()
                except IndexError:
                    # if no filename is given
                    print('Error: no filename given')
                    self.line()
            else:
                # appends the argument to the list of other args
                comment.append(args[i])
        # if not using output
        # prints the list of arguments joined by a space
        print(' '.join(comment))
        self.line()

    def do_dir(self, args):

        try:
            # if using input from a file
            if args[0] == '<':
                try:
                    # gets the contents of the given directory
                    data = os.listdir(self.from_file(args[1]))
                    data = '  '.join(data)
                    try:
                        # if using input from file and overwrite
                        if args[2] == '>':
                            try:
                                # outputs contents of the directory to the given file
                                self.overwrite(args[3], data)
                                self.line()
                            except IndexError:
                                # if no filename is given
                                print("Error: No filename given")
                                self.line()
                        # if using input from file and append
                        elif args[2] == '>>':
                            try:
                                # outputs contents of the directory to the given file
                                self.append(args[3], data)
                                self.line()
                            except IndexError:
                                # If no filename is given
                                print("Error: No filename given")
                                self.line()
                    # if using input from file and no output
                    except IndexError:
                        # print contents of directory joined by 3 spaces
                        print(data)
                        self.line()
                except FileNotFoundError:
                    # if the directory doesn't exist
                    print(f"Error: '{args[1]}' no such file")
                    self.line()
                except IndexError:
                    # if no file given for input
                    print("Error: No file given")
                    self.line()
            # if using overwrite with no directory listed
            elif args[0] == '>':
                # gets the contents of the current directory
                data = os.listdir(self.cwd)
                data = '    '.join(data)
                try:
                    # outputs contents of current dir to file
                    self.overwrite(args[1], data)
                    self.line()
                except IndexError:
                    # if no filename given
                    print("Error: No filename given")
                    self.line()
            # if using append with no directory listed
            elif args[0] == '>>':
                # gets the contents of the current directory
                data = os.listdir(self.cwd)
                data = '    '.join(data)
                try:
                    # outputs content is current dir to file
                    self.append(args[1], data)
                    self.line()
                except IndexError:
                    # if no filename given
                    print("Error: No filename given")
            # if using overwrite with a given directory
            elif args[1] == '>':
                try:
                    # gets contents of given directory
                    data = os.listdir(args[0])
                    data = '    '.join(data)
                    try:
                        # outputs content of given dir to file
                        self.overwrite(args[2], data)
                        self.line()
                    except IndexError:
                        # if no filename given
                        print('Error: No filename given')
                except FileNotFoundError:
                    # if the directory doesn't exist
                    print(f"Error: '{args[0]}' no such directory")
                    self.line()
            # if using append with a given directory
            elif args[1] == '>>':
                try:
                    # gets contents of given directory
                    data = os.list(args[0])
                    data = '    '.join(data)
                    try:
                        # outputs contents of given dir to file
                        self.append(args[2], data)
                        self.line()
                    except IndexError:
                        # if no filename given
                        print("Error: No filename given")
                        self.line()
                except FileNotFoundError:
                    # if the directory doesn't exist
                    print(f"Error: '{args[0]}' no such directory")
                    self.line()
        except IndexError:
            try:
                # If using dir from a given directory without output
                data = os.listdir(args[0])
                data = '    '.join(data)
                # prints contents of the given directory separated by 3 spaces
                print(data)
                self.line()
            except IndexError:
                # if using dir with no arguments
                data = os.listdir(os.getcwd())
                # prints the contents of the current directory separated by 3 spaces
                print('    '.join(data))
                self.line()
            except FileNotFoundError:
                # if the given file doesn't exist
                print('Error: No such directory')
                self.line()

    def from_file(self, filename):
        # returns a string with the contents of a specified file
        with open(filename, 'r') as f:
            return '\n'.join([args.strip() for args in f.readlines()])

    def overwrite(self, filename, data):
        # overwrites content of the specified file with the given data
        with open(filename, 'w+') as f:
            for a in data:
                f.write(a + '\n')

    def append(self, filename, data):
        # appedns the given data to the end of the file
        with open(filename, 'a+') as f:
            for a in data:
                f.write(a + '\n')

    def batch(self, args):
        # if using a batch file
        for command in args:
            # splits the command into seperate arguments
            command = command.split()
            try:
                # run the command as a built-in command
                self.disbatcher[command[0]](command[1:])
            except KeyError:
                # if the command isn't a built-in
                try:
                    # if forking to background
                    if args[-1] == '&':
                        for i in range(1, len(args[:-1])):
                            # if forking and overwriting
                            if args[i] == '>':
                                try:
                                    # outputs result of forked command to the given file
                                    self.overwrite(
                                              args[i+1],
                                              subprocess.Popen(args[:i])
                                             )
                                except IndexError:
                                    # if no filename is given
                                    print("Error: No filename given")
                                except FileNotFoundError:
                                    # if the command doesn't exist
                                    print('Error: No such command')
                            # if forking and appending
                            elif args[i] == '>>':
                                try:
                                    # outputs result of forked command to the given file
                                    self.append(
                                           args[i+1],
                                           subprocess.Popen(args[:i])
                                          )
                                except IndexError:
                                    # if no filename is given
                                    print("Error: No filename given")
                                except FileNotFoundError:
                                    # if the command doesn't exist
                                    print('Error: No such command')
                            else:
                                # not using IO redirection
                                try:
                                    # runs the command as a background process
                                    subprocess.Popen(args[:-1])
                                except FileNotFoundError:
                                    # if the command doesn't exist
                                    print('Error: No such command')
                    else:
                        try:
                            # runs the command as a background process
                            subprocess.run(args)
                        except FileNotFoundError:
                            # if the command doesn't exist
                            print('Error: No such command')
                except PermissionError:
                    pass

    def b_dir(self, args):
        try:
            # if using input from a file
            if args[0] == '<':
                try:
                    # gets the contents of the given directory
                    data = self.from_file(args[1])
                    data = "   ".join(os.listdir(data))
                    # if using input from file and append
                    if args[2] == '>>':
                        try:
                            # outputs contents of the directory to the given file
                            self.append(args[3], [data])
                        except IndexError:
                            # if no filename is given
                            print("Error: No filename given")
                    # if using input from file and overwrite
                    elif args[2] == '>':
                        try:
                            # outputs contents of the directory to the given file
                            self.overwrite(args[3], [data])
                        except IndexError:
                            # if no filename is given
                            print("Error: No filename given")
                except FileNotFoundError:
                    # if the input file doesn't exist
                    print("Error: No such file")
            elif args[0] == '>':
                # if using overwrite without a given directory
                try:
                    data = "   ".join(os.listdir(os.getcwd()))
                    # outputs contents of the current directory to the given file
                    self.overwrite(args[1], [data])
                except IndexError:
                    # if no filename is given
                    print("Error: No filename given")
            # if using append without a given directory
            elif args[0] == '>>':
                try:
                    data = '   '.join(os.listdir(os.getcwd()))
                    # outputs contents of the current directory to the given file
                    self.append(args[1], [data])
                except IndexError:
                    # if no filename is given
                    print("Error: No filename given")
            # if using overwrite with a specified directory
            elif args[1] == '>':
                try:
                    data = '   '.join(os.listdir(args[0]))
                    # outputs the contents of the specified directory to the file
                    self.overwrite(args[2], [data])
                except FileNotFoundError:
                    # if the given directory doesn't exist
                    print("Error: No such directory")
                except IndexError:
                    # if no filename is given
                    print("Error: No filename given")
            # if using append with a specified directory
            elif args[1] == '>>':
                try:
                    data = '   '.join(os.listdir(args[0]))
                    # outputs the contents of the specified directory to the file
                    self.append(args[2], [data])
                except FileNotFoundError:
                    # if the given directory doesn't exist
                    print("Error: No such directory")
                except IndexError:
                    # if no filename is given
                    print("Error: No filename given")
        except IndexError:
            # if not using output or input
            try:
                data = '   '.join(os.listdir(args[1]))
                # prints the contents of the specified directory separated by 3 spaces
                print(data)
            except IndexError:
                # if no arguments are provided
                data = '   '.join(os.listdir(os.getcwd()))
                # prints the contents of the current directory separated by 3 spaces
                print(data)

    def b_echo(self, args):
        comment = []
        for i in range(1, len(args)):
            # if using overwrite
            if args[i] == '>':
                try:
                    # outputs the comment to the given file
                    comment = " ".join(comment)
                    self.overwrite(args[i+1], comment)
                    return
                except IndexError:
                    # if no filename is given
                    print("Error: No filename given")
                    return
            # if using append
            elif args[i] == '>>':
                try:
                    # outputs the comment to the given file
                    comment = " ".join(comment)
                    self.append(args[i+1], comment)
                    return
                except IndexError:
                    # if no filename is given
                    print("Error: No filename given")
                    return
            else:
                # appends the argument to the list of other args
                comment.append(args[i])
        # if not using output
        # prints the list of arguments joined by a space
        comment = " ".join(comment)
        print(comment)

    def b_cd(self, args):
        try:
            # changes directory to the given directory
            os.chdir(args[0])
            # $CWD points to current directory
            os.environ['PWD'] = os.getcwd()
            curr_dir = os.getcwd()
            # changes the promtp to the current directory
            if os.environ['HOME'] in curr_dir:
                # if $HOME in the directory, shorten to ~/
                curr_dir = '~' + curr_dir[len(os.environ['HOME']):]
            user = os.environ['USER']
            host = os.uname()[1]
            # update prompt
            self.prompt = f"{user}@{host} {curr_dir}$ "
        except FileNotFoundError:
            # If the directory doesn't exist
            print("Error: no such directory")
        except IndexError:
            # if using cd without and argument
            # prints the current directory
            print(os.getcwd())

    def b_quit(self, args):
        # exits the shell
        exit()

    def b_env(self, args):

        try:
            # if using output
            if args[0] == '>':
                try:
                    data = os.environ
                    data_list = []
                    for a in data:
                        # outputs environment strings to the given file
                        data_list.append(f"{a}:{data[a]}")
                    self.overwrite(args[1], data_list)
                except IndexError:
                    # if no filename is given
                    print('Error: No filename given')
            # if using append
            elif args[0] == '>>':
                try:
                    data = os.environ
                    data_list = []
                    for a in data:
                        # outputs environment strings to the given file
                        data_list.append(f"{a}:{data[a]}")
                    self.append(args[1], data_list)
                except IndexError:
                    # if no filename is given
                    print('Error: No filename given')
        except IndexError:
            # if no output is used
            data = os.environ
            for a in data:
                # prints environment strings to the terminal
                print(f"{a}:{data[a]}")


if __name__ == "__main__":
    try:
        with open(sys.argv[1], 'r') as f:
            # takes the lines from the input as a list
            commands = f.readlines()
            # appends quit to the end of the commands to close the shell after the batch is complete
            commands.append('quit' + '\n')
            # initialises the shell
            shell = MyShell()
            # runs the batch file
            shell.batch(commands)
    except FileNotFoundError:
        # if the batch file given doesn't exist
        print('No such file')
    except IndexError:
        # otherwise open the shell as normal
        MyShell().pre()
# Sean Moloney 17477122
