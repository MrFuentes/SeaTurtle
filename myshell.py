#!/usr/bin/env python3.7
from cmd import Cmd
import subprocess
import os
import sys


class SeaTurtle(Cmd):
    '''\nWaits for a command line input,\
 then executes the input when it is recieved\n'''
    # Promt that comes up when the shell is launched
    intro = 'Type "help" to bring up a list of commands.\n'
    # Sets $SHELL to "(LaunchDirectory)/MyShell"
    os.environ['SHELL'] = os.getcwd()+'/MyShell'
    if os.environ['HOME'] == os.getcwd()[0:len(os.environ['HOME'])]:
        # If CWD is in $HOME(/home/user/) display $HOME as "~/"
        prompt = '{}@{} ~{} $ '.format(
                                       os.environ['USER'],
                                       os.uname()[1],
                                       os.getcwd()[len(os.environ['HOME']):]
                                      )
    else:
        # otherwise display true directory
        prompt = '{}@{} {} $ '.format(
                                      os.environ['USER'],
                                      os.uname()[1],
                                      os.getcwd()
                                     )

    def emptyline(self, arg=None):
        print('',end='')

    def default(self, arg):

        '''\nRuns as a subprocess if the command is not built in\n'''
        args = parse(arg)
        try:
            if args[-1] == '&':
                # Runs program as a background process
                for i in range(0, len(args[:-1])):
                    if args[i] == '>':
                        # Using overwrite output
                        try:
                            overwrite(subprocess.Popen(args[:i]), args[i+1:])
                        except IndexError:
                            # If no filename given
                            print('Error: No filename given')
                    elif args[i] == '>>':
                        # Using append overwrite
                        try:
                            append(subprocess.Popen(args[:i], args[i+1]))
                        except IndexError:
                            # If no filename given
                            print('Error: No filename given')
                    else:
                        try:
                            subprocess.Popen(args[:-1])
                        except FileNotFoundError:
                            # If the command doesn't exist
                            print('Error: No such command')
            else:
                try:
                    subprocess.run(args)
                except FileNotFoundError:
                    # If the command doesn't exist
                    print('Error: No such command')
        except IndexError:
            # If command with no arguments given
            try:
                subprocess.run(args)
            except FileNotFoundError:
                # If the command doesn't exist
                print('Error: No such command')

    def do_dir(self, arg):
        '''\nlists the contents of a directory, \
or prints the current directory if no arguemts are given\n'''
        # Gets list of command line arguments
        args = parse(arg)
        try:
            # if using standard input
            if args[0] == '<':
                try:
                    # Use contents of input file as directory
                    data = from_input(args[1])
                    try:
                        # If using output to append data
                        if args[2] == '>>':
                            try:
                                # append contents to the file
                                append(ls_dir(data[0]), args[3:])
                            except IndexError:
                                # If no filename specified
                                print('Error: No filename given')
                                string = 'Usage: dir < {} >> <filename>'
                                string = string.format(data[0])
                                print(string)

                        elif args[2] == '>':
                            try:
                                # overwrite the data in the file
                                overwrite(ls_dir(data[0]), args[3:])
                            except IndexError:
                                # If no filename specified
                                print('Error: No filename given')
                                string = 'Usage: dir < {} >> <filename>'
                                string = string.format(data[0])
                                print(string)
                        else:
                            # If standard output not being used
                            # Prints content
                            print(ls_dir(data[0]))
                    except IndexError:
                        # If standard output not being used
                        # Prints content
                        print(ls_dir(data[0]))
                except IndexError:
                    # shows this error message if no filename was specified
                    print('Error: No filename given')
                    print('Usage: dir < <filename>')
            elif args[1] == '>>':
                # If using append output with a specific directory
                try:
                    # Appends to the filename specified
                    append(ls_dir(args[0]), args[2:])
                except IndexError:
                    # Shows this error if no filename is specified
                    print('Error: No filename given')
                    print('Usage: dir {} >> <filename>'.format(args[0]))
            elif args[1] == '>':
                # If using overwrite output with a specific directory
                try:
                    # Overwrites the contents of the listed directory
                    overwrite(ls_dir(args[0]), args[2:])
                except IndexError:
                    # Shows this error if no filename is specified
                    print('Error: No filename given')
                    print('Usage: dir {} > <filename>'.format(args[0]))
                # If using append output without a specified directory
            elif args[0] == '>>':
                try:
                    # Append to the specified file
                    append([ls_dir()], args[1:])
                except IndexError:
                    # If no filename is specified
                    print('Error: No filename given')
                    print('Usage: dir >> <filename>')
            elif args[0] == '>':
                # If using overwrite without a specified directory
                try:
                    # Overwrites file's contents
                    overwrite([ls_dir()], args[1:])
                except IndexError:
                    # If no filename is specified
                    print('Error: No filename given')
                    print('Usage: dir > <filename>')
            else:
                # prints the content of the specified directory
                print(ls_dir(args[0]))
        except IndexError:
            # Prints the content of the current directory
            print(ls_dir())

    def do_clr(self, arg):

        '''\nClears the terminal\n'''
        print("\x1b[J\x1b[H")

    def do_echo(self, arg):

        '''\nPrints the arguments to the terminal\n'''
        args = parse(arg)
        comment = []
        count = 0
        for i in range(0, len(args)):
            # If using overwrite
            if args[i] == '>':
                # concatenate preceding arguments to a string
                echoed = get_echo(comment)
                try:
                    # outputs the string to the given file
                    overwrite([echoed], args[i+1:])
                    break
                except IndexError:
                    # prints this error message if no filename is given
                    print('Error: No filename given')
                    print('Usage: echo <comment> > <filename>')
                    break
            # If using append
            elif args[i] == '>>':
                # concatenate preceding arguments to a string
                echoed = get_echo(comment)
                try:
                    # outputs the string to the given file
                    append([echoed], args[i+1:])
                    break
                except IndexError:
                    # shows this error if no filename is given
                    print('Error: No filename given')
                    print('Usage: echo <comment> >> <filename>')
                    break
            else:
                # appends arguments that are not output commands to a list
                comment.append(args[i])
                count += 1
        # If the loop did not break early
        if count == len(args):
            # Print the concatenated list of arguments as a string
            print(get_echo(comment))

    def do_cd(self, arg):

        '''\nchanges directory do given directory or \
display current directory if no directroy is given\n'''
        args = parse(arg)
        try:
            # changes directory to given directory
            os.chdir(args[0])
            os.environ['PWD'] = os.getcwd()
            curr_dir = os.getcwd()[0:len(os.environ['HOME'])]
            if os.environ['HOME'] == curr_dir:
                # If CWD is in $HOME(/home/user/) display $HOME as "~/"
                ndir = os.getcwd()[len(os.environ['HOME']):]
                user = os.environ['USER']
                host = os.uname()[1]
                SeaTurtle.prompt = '{}@{} ~{} $ '.format(user, host, ndir)
            else:
                # otherwise display true directory
                ndir = os.getcwd()
                user = os.environ['USER']
                host = os.uname()[1]
                SeaTurtle.prompt = '{}@{} {} $ '.format(user, host, ndir)
        except FileNotFoundError:
            # displays this error message if the given file does not exist
            print('Error: No such directory')
        except IndexError:
            print(os.getcwd())
            # if no directory is given, change directory to $HOME
            # os.chdir(os.environ['HOME'])
            # home = os.getcwd()[len(os.environ['HOME']):]
            # user = os.environ['USER']
            # host = os.uname()[1]
            # SeaTurtle.prompt = '{}@{} ~{} $ '.format(user, host, home)

    def do_environ(self, arg):

        '''\nprints all environment variables, separated by a newline\n'''
        # converts arg to a list
        args = parse(arg)
        try:
            # If using overwrite
            if args[0] == '>':
                try:
                    # Output environment strings to the specified file
                    overwrite(get_environ(), args[1:])
                except IndexError:
                    # Print this Error message if no filename is given
                    print('Error: No filename given')
                    print('Usage: environ > <filename>')
            # If using append
            elif args[0] == '>>':
                try:
                    # Appends output to the given file
                    append(get_environ(), args[1:])
                except IndexError:
                    # Print this Error message if no filename is given
                    print('Error: No filename given')
                    print('Usage: environ >> <filename>')
        except IndexError:
            print("\n".join(get_environ()))

    def do_pause(self, arg):

        '''\nPause shell functions until return key is pressed\n'''
        input()

    def do_quit(self, arg):

        '''\nExits the shell\n'''
        exit()


def get_environ():

    '''\nreturns a list containing all the environment \
variables and their values as strings\n'''
    env_list = []
    for k in os.environ:
        env_list.append('{} : {}'.format(k, os.environ[k]))
    return env_list


def get_echo(comment):

    '''\nConcatenates a list to a single string\n'''
    return " ".join(comment)


def ls_dir(directory=None):

    '''\nReturns the contents of a directory as a string\n'''
    try:
        # If a directory is specified
        if directory is not None:
            # Return a string containing all the contents
            return "\n".join([f for f in os.listdir(directory)])
        # If no directory is specified
        else:
            # Return a string containing the contents of the current directory
            return '\n'.join([f for f in os.listdir(os.getcwd())])
    except FileNotFoundError:
        # Shows this error message if the directory does not exist
        print('Error: Directory "{}" not found'.format(directory))


def from_input(filename):

    '''\ngets content from the specified file and returns it as a list\n'''
    try:
        with open(filename, 'r') as f:
            # returns a list of all the lines contained in the file
            return [args.strip() for args in f.readlines()]
    except FileNotFoundError:
        # Shows this error message if the file does not exist
        print('Error: File "{}" not found'.format(filename))


def overwrite(data, args):

    '''\noverwrites any data within a file with new data, \
or creates a new file containing the new data if one doesn't exist\n'''
    try:
        # Opens the file, or creates one with that name if it doesn't exist
        with open(args[0], 'w+') as f:
            for a in data:
                # Writes the data to the file
                f.write(a)
                # Adds a newline character to the end of the file
                f.write('\n')
    except IndexError:
        # Shows this error message if no file was specified
        print('Usage: <command> > <filename>')


def append(data, args):

    '''\nappends new data to a file, or creates a file containing the new data if \
one does not exist\n'''
    try:
        # Opens the file, or creates one with that name if it doesn't exist
        with open(args[0], 'a+') as f:
            for a in data:
                # Writes the data to the file
                f.write(a)
                # Adds a newline charater to the end of the file
                f.write('\n')
    except IndexError:
        # Shows this error message if no filename was specified
        print('Usage: <command> >> <filename>')


def parse(arg):

    '''\nGets the command line arguments and returns them as list without the \
original command\n'''
    return arg.split()


if __name__ == "__main__":
    try:
        # If using batch file
        with open(sys.argv[1], 'r') as f:
            st = SeaTurtle()
            queue = f.readlines()
            queue.append('quit')
            st.cmdqueue = queue
            st.intro = None
            st.cmdloop()
    except IndexError:
        SeaTurtle().cmdloop()
