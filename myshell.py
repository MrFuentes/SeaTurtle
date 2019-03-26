#!/usr/bin/env python3.7
from cmd import Cmd
import subprocess
import os


class SeaTurtle(Cmd):
    '''Waits for a command line input,
    then executes the input when it is recieved'''
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

    def default(self, arg):

        args = parse(arg)
        try:
            if args[-1] == '&':
                for i in range(0, len(args[:-1])):
                    if args[i] == '>':
                        try:
                            overwrite(subprocess.Popen(args[:i]), args[i+1:])
                        except IndexError:
                            print('Error: No filename given')
                    elif args[i] == '>>':
                        try:
                            append(subprocess.Popen(args[:i], args[i+1]))
                        except IndexError:
                            print('Error: No filename given')
                    else:
                        try:
                            subprocess.Popen(args[:-1])
                        except FileNotFoundError:
                            print('Error: No such command')
            else:
                try:
                    subprocess.run(args)
                except FileNotFoundError:
                    print('Error: No such command')
        except IndexError:
            try:
                subprocess.run(args)
            except FileNotFoundError:
                print('Error: No such command')

        def do_dir(self, arg):
            '''lists the contents of a directory,
            or prints the current directory if no arguemts are given'''
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
                                    string = 'Usage: dir < {} >> <filename>'.format(data[0])
                                    print(string)

                            elif args[2] == '>':
                                try:
                                    # overwrite the data in the file
                                    overwrite(ls_dir(data[0]), args[3:])  
                                except IndexError:
                                    # Shows this error message if no filename specified
                                    print('Error: No filename given')
                                    print('Usage: dir < {} >> <filename>'.format(data[0]))
                            else:  
                                # Prints the contents if standard output not being used
                                print(ls_dir(data[0]))
                        except IndexError:
                        print(ls_dir(data[0]))  # Prints the contents if standard output not being used
                    except IndexError:
                            print('Error: No filename given')
                            print('Usage: dir < <filename>')  # shows this error message if no filename was specified
                elif args[1] == '>>':  # If using append output with a specific directory
                    try:
                        append(ls_dir(args[0]),args[2:])  # Appends the content from the named directory to the filename specified
                    except IndexError:
                        print('Error: No filename given')
                        print('Usage: dir {} >> <filename>'.format(args[0])) # Shows this error if no filename is specified 
                elif args[1] == '>':  # If using overwrite output with a specific directory
                    try:
                        overwrite(ls_dir(args[0]),args[2:])  # Overwrites the file's content with the contents of the listed directory
                    except IndexError:
                        print('Error: No filename given')
                        print('Usage: dir {} > <filename>'.format(args[0]))  # Shows this error if no filename is specified
            except IndexError:
                try:
                    if args[0] == '>>':  # If using append output without a specified directory
                        try:
                            append(ls_dir(),args[1:])  # Append the content of the current directory to the specified file
                        except IndexError:
                            print('Error: No filename given')
                            print('Usage: dir >> <filename>')  # Shows this error message if no filename is specified
                    elif args[0] == '>':  # If using overwrite output without a specified directory
                        try:
                            overwrite(ls_dir(),args[1:])  # Overwrites file's contents with the content of the current directory
                        except IndexError:
                            print('Error: No filename given')
                            print('Usage: dir > <filename>')  # Shows this error message if no filename is specified
                    else:
                        print(ls_dir(args[0]))  # prints the content of the specified directory
                except IndexError:
                    print(ls_dir())  # Prints the content of the current directory if no directory is specified

        

        def do_clr(self, arg):
                

            '''Clears the terminal'''
            os.system('clear') # clears the terminal


        def do_echo(self,arg):
                

            '''Prints the arguments to the terminal'''
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
                        overwrite([echoed],args[i+1:])
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
                        append([echoed],args[i+1:])
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
            # If the loop did not break early, meaning there were no output commands
            if count == len(args):
                # Print the concatenated list of arguments as a string
                print(get_echo(comment))


        def do_cd(self,arg):

            '''changes directory do given directory or display current directory if no directroy is given'''
            args = parse(arg)
            try:
                # changes directory to given directory
                os.chdir(args[0])
                os.environ['PWD'] = os.getcwd()
                if os.environ['HOME'] == os.getcwd()[0:len(os.environ['HOME'])]:        
                    # If CWD is in $HOME(/home/user/) display $HOME as "~/"
                    SeaTurtle.prompt = '{}@{} ~{} $ '.format(os.environ['USER'],os.uname()[1],os.getcwd()[len(os.environ['HOME']):])
                else:
                    # otherwise display true directory
                    SeaTurtle.prompt = '{}@{} {} $ '.format(os.environ['USER'],os.uname()[1],os.getcwd())
            except FileNotFoundError:
                # displays this error message if the given file does not exist
                print('Error: No such directory')
            except IndexError:
                print(os.getcwd())
                # if no directory is given, change directory to $HOME
                #os.chdir(os.environ['HOME'])
                #SeaTurtle.prompt = '{}@{} ~{} $ '.format(os.environ['USER'],os.uname()[1],os.getcwd()[len(os.environ['HOME']):])


        def do_environ(self, arg):
                
            '''prints all environment variables, separated by \n'''
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


        def do_quit(self,arg):

            '''Exits the shell'''
            exit()


def get_environ():


    '''returns a list containing all the environment variables and their values as strings'''
    env_list = []
    for k in os.environ:
        env_list.append('{} : {}'.format(k, os.environ[k]))     
    return env_list


def get_echo(comment):


    '''Concatenates a list to a single string'''
    return " ".join(comment)


def ls_dir(directory=None):


    '''Returns the contents of a directory as a string'''
    try:
        # If a directory is specified
        if  directory != None:
            # Return a string containing all the contents of the specified directory
            return  "\n".join([f for f in os.listdir(directory)])
        # If no directory is specified
        else:
            # Return a string containing the contents of the current directory
            return '\n'.join([f for f in os.listdir()])
    except FileNotFoundError:
        # Shows this error message if the directory does not exist
        print('Error: Directory "{}" not found'.format(directory))
                


def from_input(filename):
        

    '''gets content from the specified file and returns it as a list'''
    try:
        with open(filename,'r') as f:
            return [args.strip() for args in f.readlines()] # returns a list of all the lines contained in the file
    except FileNotFoundError:
        print('Error: File "{}" not found'.format(filename))  # Shows this error message if the file does not exist


def overwrite(data,args):


    '''overwrites any data within a file with new data, or creates a new file containing the new data if one doesn't exist'''
    try:
        # Opens the file, or creates one with that name if it doesn't exist
        with open(args[0], 'w+') as f:
            for a in data:
                # Writes the data to the file, overwriting any data that was already contained by the file 
                f.write(a)
                # Adds a newline character to the end of the file
                f.write('\n')
        except IndexError:
                # Shows this error message if no file was specified
                print('Usage: <command> > <filename>')


def append(data,args):

    '''appends new data to a file, or creates a file containing the new data if one does not exist'''
    try:
        # Opens the file, or creates one with that name if it doesn't exist
        with open(args[0], 'a+') as f:
            for a in data:
                # Writes the data to the file, appending to the end of the file if there was already data within the file
                f.write(a)
                # Adds a newline charater to the end of the file
                f.write('\n')
    except IndexError:
        # Shows this error message if no filename was specified
        print('Usage: <command> >> <filename>')

        
def parse(arg):
        
    '''Gets the command line arguments and returns them as list without the orinal command'''
    return arg.split()


if __name__ == "__main__":
    SeaTurtle().cmdloop()
