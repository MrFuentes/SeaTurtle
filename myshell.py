'''
 
 To Do:
 =======================================================================
 help: display user manual
 pause: pause operation of shell until 'Enter' is pressed
 all other commands fork programs into it's child processes
 must be able to take input form a file/batchfile implementation
 & executes program as backgroud process
 -----------------------------------------------------------------------
 
 In Progress:
 =======================================================================
 environ: list all environment strings
 -----------------------------------------------------------------------
 
 Maybe ImplementedL
 =======================================================================
 ??? shell=<pathname>/myshell where path is where shell was executed ???
 -----------------------------------------------------------------------
 
 Implemented:
 =======================================================================
 quit: exit the shell
 dir <directory>: list directory contents
 > truncates existing file or creates new file
 i/o redirection: program >> file / program > file
 < file as input
 >> appends existing file or creates new file
 clr: clear screen
 echo <comment>: print <comment> to command line followed by a \n
 cd <directory>: change directory
 -----------------------------------------------------------------------

'''

#!/usr/bin/env python3

from cmd import Cmd
import multiprocessing
import os
import sys


class MyShell(Cmd):


	'''
 	
	MyShell
	=======

	Waits for a command line input, then executes the input when it is recieved

	Commands
	--------

	dir <directory_name>: Lists the contents of the named directory, or the current directory if no directory is specified
	
	<command> < <file_name>: Uses the listed file's content as the input for the command
	
	<command> <paramters> > <file_name>: Writes the output of the specified command to the listed file, overwriting any existing data, or creating a new file if it doesn't exist

	<command> <parameters> >> <file_name>: Writes the output of the specified command to the listed file, appending to any existing data, or creating a new file if it doesn't exist

	quit: Exits the shell

	Variables
	---------

	intro: str
		> String that is printed when the shell is launched
	
	prompt: str
		> Lists the username, hostname and currrent directory
		> If in $HOME shortens $HOME to "~/"

	'''


	intro = 'Type "help" to bring up a list of commands.\n'	 # Promt that comes up when the shell is launched
	os.environ['SHELL'] = os.getcwd()+'/MyShell'  # Sets $SHELL to "(LaunchDirectory)/MyShell" 
	if os.environ['HOME'] == os.getcwd()[0:len(os.environ['HOME'])]:
		prompt = '{}@{} ~{} $ '.format(os.environ['USER'],os.uname()[1],os.getcwd()[len(os.environ['HOME']):])  # If CWD is in $HOME(/home/user/) display $HOME as "~/"
	else:
		prompt = '{}@{} {} $ '.format(os.environ['USER'],os.uname()[1],os.getcwd())  # otherwise display true directory
	file = None

	def do_dir(self,arg):
		

		'''
		
		do_dir
		======
		
		lists directory content when "dir" is typed into the shell

		Parameters
		----------

		directory:
			> If present in arguments, will list the contents of that directory
			> Else it will list the contents of the current directory

		'''


		args = parse(arg)  # Gets list of command line arguments
		try:
			if args[0] == '<':  # if using standard input
				try:
					data = from_input(args[1])  # Use contents of input file as directory
					try:
						if args[2] == '>>':  # If using output to append data
							try:
								append(ls_dir(data[0]),args[3:])  # append contents to the file
							except IndexError:
								print('Error: No filename given')
								print('Usage: dir < {} >> <filename>'.format(data[0]))  # Shows this error message if no filename specified
						elif args[2] == '>':
							try:
								overwrite(ls_dir(data[0]), args[3:])  # overwrite the data in the file with the contents
							except IndexError:
								print('Error: No filename given')
								print('Usage: dir < {} >> <filename>'.format(data[0]))  # Shows this error message if no filename specified
						else:
							print(ls_dir(data[0]))  # Prints the contents if standard output not being used
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

		#get_dir = multiprocessing.Process(target=ls_dir, args=(arg,))
		#get_dir.start()
	

	def do_clr(self, arg):
		
		'''

		do_clr
		======

		Clears the terminal when "clr" is typed into the shell

		'''

		os.system('clear') # clears the terminal


	def do_echo(self,arg):
		
		'''
		
		do_echo
		=======

		Prints the arguments to the terminal

		Paramters
		---------
		
		arg
			> command line arguemnts to be joined into a string

		Output
		------

		Outputs the arguments following the command as a string

		'''

		args = parse(arg)
		comment = []
		count = 0
		for i in range(0, len(args)):
			if args[i] == '>':  # If using overwrite
				echoed = get_echo(comment)  # concatenate preceding arguments to a string
				try:
					overwrite([echoed],args[i+1:])  # outputs the string to the given file
					break
				except IndexError:
					print('Error: No filename given')  # prints this error message if no filename is given
					print('Usage: echo <comment> > <filename>')
					break
			elif args[i] == '>>':  # If using append
				echoed = get_echo(comment)  # concatenate preceding arguments to a string
				try:
					append([echoed],args[i+1])  # outputs the string to the given file
					break
				except IndexError:
					print('Error: No filename given')  # shows this error if no filename is given
					print('Usage: echo <comment> >> <filename>')
					break
			else:
				comment.append(args[i])  # appends arguments that are not output commands to a list
				count += 1
		if count == len(args):  # If the loop did not break early, meaning there were no output commands
			print(get_echo(comment))  # Print the concatenated list of arguments as a string


	def do_cd(self,arg):

		'''

		do_cd
		=====

		changes directory do given directory or $HOME if no directroy is given

		'''

		args = parse(arg)
		try:
			os.chdir(args[0])  # changes directory to given directory
			if os.environ['HOME'] == os.getcwd()[0:len(os.environ['HOME'])]:	
				MyShell.prompt = '{}@{} ~{} $ '.format(os.environ['USER'],os.uname()[1],os.getcwd()[len(os.environ['HOME']):])  # If CWD is in $HOME(/home/user/) display $HOME as "~/"
			else:
				MyShell.prompt = '{}@{} {} $ '.format(os.environ['USER'],os.uname()[1],os.getcwd())  # otherwise display true directory
		except FileNotFoundError:
			print('Error: No such directory')  # displays this error message if the given file does not exist
		except IndexError:
			os.chdir(os.environ['HOME'])  # if no directory is given, change directory to $HOME
			if os.environ['HOME'] == os.getcwd()[0:len(os.environ['HOME'])]:	
				MyShell.prompt = '{}@{} ~{} $ '.format(os.environ['USER'],os.uname()[1],os.getcwd()[len(os.environ['HOME']):])  # If CWD is in $HOME(/home/user/) display $HOME as "~/"
			else:
				MyShell.prompt = '{}@{} {} $ '.format(os.environ['USER'],os.uname()[1],os.getcwd())  # otherwise display true directory


	def do_environ(self, arg):
		
		'''
		
		do_environ
		==========

		prints all environment variables, separated by \n when 'environ' is typed into the command line
		
		'''

		args = parse(arg)  # converts arg to a list
		try:
			if args[0] == '>':  # If using overwrite
				try:
					overwrite(get_environ(), args[1:])  # Output environment strings to the specified file
				except IndexError:
					print('Error: No filename given')  # Print this Error message if no filename is given
					print('Usage: environ > <filename>')
			elif args[0] == '>>':  # If using append
				try:	
					append(get_environ(), args[1:])  # 
				except IndexError:
					print('Error: No filename given')  # Print this Error message if no filename is given
					print('Usage: environ >> <filename>')
		except IndexError:
			print("\n".join(get_environ()))


	def do_quit(self,arg):

		'''

		do_exit
		=======

		Exits the shell when "quit" is typed into the shell

		'''

		exit()


def get_environ():

	'''

	get_environ
	===========

	returns a list containing all the environment variables and their values as strings
	
	'''
	
	env_list = []
	for k in os.environ:
		env_list.append('{} : {}'.format(k, os.environ[k]))	
	return env_list


def get_echo(comment):

	'''

	get_echo
	========

	Concatenates a list to a single string

	parameters
	----------

	comment
		> list containing the data you want to concatenate to a string

	output
	------

	Returns a string of the contents of the given list

	'''

	return " ".join(comment)


def ls_dir(directory=None):

	'''
	
	ls_dir
	======

	Returns the contents of a directory as a string

	Parameters
	----------

	directory
		> directory who's contents you want to get
		> defaults to current directory

	Output
	------

	Outputs a string containing all the contents of <directory> joined by a newline character

	'''

	try:
		if  directory != None:  # If a directory is specified
			return  "\n".join([f for f in os.listdir(directory)]) # Return a string containing all the contents of the specified directory
		else:   # If no directory is specified
			return '\n'.join([f for f in os.listdir()])  # Return a string containing the contents of the current directory

	except FileNotFoundError:
		print('Error: Directory "{}" not found'.format(directory))  # Shows this error message if the directory does not exist
		


def from_input(filename):
	
	'''

	from_input
	==========

	gets content from the specified file and returns it as a list

	Parameters
	----------

	filename
		> filename you want to get the content from

	Output
	------

	returns a list of the content from <filename>

	'''

	try:
		with open(filename,'r') as f:
			return [args.strip() for args in f.readlines()] # returns a list of all the lines contained in the file
	except FileNotFoundError:
		print('Error: File "{}" not found'.format(filename))  # Shows this error message if the file does not exist


def overwrite(data,args):

	'''

	overwrite
	=========

	overwrites any data within a file with new data, or creates a new file containing the new data if one doesn't exist

	Parameters
	----------

	data
		> List of data you want to write to the file
	
	args
		> List containg the filename to write to

	'''

	try:
		with open(args[0], 'w+') as f:  # Opens the file, or creates one with that name if it doesn't exist
			for a in data:
				f.write(a)  # Writes the data to the file, overwriting any data that was already contained by the file 
			f.write('\n')  # Adds a newline character to the end of the file
	except IndexError:
		print('Usage: <command> > <filename>')  # Shows this error message if no file was specified


def append(data,args):

	'''

	append
	======

	appends new data to a file, or creates a file containing the new data if one does not exist

	Parameters
	----------

	data
		> List of data you want to write to the file

	args
		> List containing the filename to write to

	'''

	try:
		with open(args[0], 'a+') as f:  # Opens the file, or creates one with that name if it doesn't exist
			for a in data:
				f.write(a)  # Writes the data to the file, appending to the end of the file if there was already data within the file
			f.write('\n')  # Adds a newline charater to the end of the file
	except IndexError:
		print('Usage: <command> >> <filename>')  # Shows this error message if no filename was specified

	
def parse(arg):
	
	'''

	parse
	=====

	Gets the command line arguments and returns them as list without the orinal command

	Parameters
	----------

	arg
		> command line arguments entered after the command

	Output
	------

	Returns a list containing all command line arguments after the original command

	'''

	return arg.split()

if __name__ == "__main__":
	MyShell().cmdloop()
