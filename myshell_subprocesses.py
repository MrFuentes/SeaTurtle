# Notes:
# Use Subprocessor module
# User Manual is important


# todo:
# help: display user manual
# pause: pause operation of shell until 'Enter' is pressed
# all other commands fork programs into it's child processes
# must be able to take input form a file/batchfile implementation
# & executes program as backgroud process
# clr: clear screen
# echo <comment>: print <comment> to command line followed by a \n
# cd <directory>: change directory
# environ: list all environment strings

# Maybe Implemented:
# ??? shell=<pathname>/myshell where path is where shell was executed ???

# Implemented:
# quit: exit the shell
# dir <directory>: list directory contents
# > truncates existing file or creates new file
# i/o redirection: program >> file / program > file
# < file as input
# >> appends existing file or creates new file



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


	intro = 'Type "help" to bring up a list of commands.\n'		# Promt that comes up when the shell is launched
	os.environ['SHELL'] = os.getcwd()+'/MyShell'		# Sets $SHELL to "(LaunchDirectory)/MyShell" 
	if os.environ['HOME'] == os.getcwd()[0:len(os.environ['HOME'])]:	
		prompt = '{}@{} ~{} $ '.format(os.environ['USER'],os.uname()[1],os.getcwd()[len(os.environ['HOME']):])		# If CWD is in $HOME(/home/user/) display $HOME as "~/"
	else:
		prompt = '{}@{} {} $ '.format(os.environ['USER'],os.uname()[1],os.getcwd())		# otherwise display true directory
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
								print('Usage: dir < {} >> <filename>'.format(data[0]))  # Shows this error message if no filename specified
						elif args[2] == '>':
							try:
								overwrite(ls_dir(data[0]), args[3:])  # overwrite the data in the file with the contents
							except IndexError:
								print('Usage: dir < {} >> <filename>'.format(data[0]))  # Shows this error message if no filename specified
						else:
							print(ls_dir(data[0]))  # Prints the contents if standard output not being used
					except IndexError:
						print(ls_dir(data[0]))  # Prints the contents if standard output not being used
				except IndexError:
					print('Usage: dir < <filename>')  # shows this error message if no filename was specified
			elif args[1] == '>>':  # If using append output with a specific directory
				try:
					append(ls_dir(args[0]),args[2:])  # Appends the content from the named directory to the filename specified
				except IndexError:
					print('Usage: dir {} >> <filename>'.format(args[0])) # Shows this error if no filename is specified 
			elif args[1] == '>':  # If using overwrite output with a specific directory
				try:
					overwrite(ls_dir(args[0]),args[2:])  # Overwrites the file's content with the contents of the listed directory
				except IndexError:
					print('Usage: dir {} > <filename>'.format(args[0]))  # Shows this error if no filename is specified
			elif args[0] == '>>':  # If using append output without a specified directory
				try:
					append(ls_dir(),args[1:])  # Append the content of the current directory to the specified file
				except IndexError:
					print('Usage: dir >> <filename>')  # Shows this error message if no filename is specified
			elif args[0] == '>':  # If using overwrite output without a specified directory
				try:
					overwrite(ls_dir(),args[1:])  # Overwrites file's contents with the content of the current directory
				except IndexError:
					print('Usage: dir > <filename>')  # Shows this error message if no filename is specified
			else:
				try:
					print(ls_dir(args[0]))  # prints the content of the specified directory
				#except TypeError:
				#	print(ls_dir())
		except IndexError:
			print(ls_dir())  # Prints the content of the current directory if no directory is specified

		#get_dir = multiprocessing.Process(target=ls_dir, args=(arg,))
		#get_dir.start()
	

	def do_quit(self,arg):

		'''
		do_exit
		=======

		Exits the shell when "quit" is typed into the shell

		'''

		exit()


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
			return ('\n'.join([f for f in os.listdir()])  # Return a string containing the contents of the current directory
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
	try:
		with open(args[0], 'w+') as f:
			for a in data:
				f.write(a)
			f.write('\n')
	except IndexError:
		print('Usage: <command> > <filename>')


def append(data,args):
	try:
		with open(args[0], 'a+') as f:
			for a in data:
				f.write(a)
			f.write('\n')
	except IndexError:
		print('Usage: <command> >> <filename>')

	
def parse(arg):
	# Convert arguments into a list
	return arg.split()

if __name__ == "__main__":
	MyShell().cmdloop()
