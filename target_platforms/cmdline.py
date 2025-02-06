from . import base
import os
import shutil
import platform
import sys
from colorama import Fore, Style
import click

class CLI(base.Base):
    index_content = '''
# Documentation: 
# https://click.palletsprojects.com/en/8.1.x/

from logging import exception
import click
import sys
import os

STRING = ''
CHOICE = ''

@click.group()
def cli():
    \'''
Example CLI tool
    \'''
    ##Running checks on python version
    version = '.'.join(sys.version.split(' ')[0].split('.')[:2])
    if float(version) < 3.0:
        raise Exception('Please use Python3+. Make sure you have created a virtual environment.')

@click.command(help='Runs CLI tool')
@click.option(
    '--string',
    '-s',
    required=True,
    help='String to return'
    )

@click.option(
    '--choice-list',
    '-c',
    type=click.Choice(
        ['1', '2', '3'], 
        case_sensitive=False
        ),
    multiple=True, 
    default=['1'], 
    help="Select numbers you would like to return (ie. -c 1 -c 2 -c 3)"
    )
def run(string,choice_list):
    STRING=string
    CHOICE=choice_list
    print('String entered = '+ STRING)
    print('Choices entered =')
    for choice in choice_list:
      print(choice)

def main():
    cli.add_command(run) #Add command for cli
    cli() #Run cli

if __name__ == '__main__':
    main()



'''

    init_content = '''
import sys
import os
# Add the parent directory of 'target_platforms' to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))'''

    def __init__(self, name, lang=''):
        self.name = name
        self.lang = lang
        if self.lang == 'py':
            self.main_content = f'''
from {self.name} import {self.name}

def main():
    {self.name}.main()

if __name__ == "__main__":
    main()
'''
        else:
            self.main_content = r'''
package main

import (
	"fmt"
	"os"
	"strconv"

	"github.com/spf13/cobra"
)

// Root command (base command `'''+self.name+r'''`)
var rootCmd = &cobra.Command{
	Use:   "'''+self.name+r'''",
	Short: "'''+self.name+r''' CLI - A simple command-line tool",
	Long:  "'''+self.name+r''' is a CLI application that provides useful commands such as greeting users and performing math operations.",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Welcome to '''+self.name+r''' CLI! Use `'''+self.name+r''' --help` to see available commands.")
	},
}

// `greet` command
var greetCmd = &cobra.Command{
	Use:   "greet",
	Short: "Greet a user",
	Long:  "This command greets the user with a friendly message.",
	Run: func(cmd *cobra.Command, args []string) {
		name, _ := cmd.Flags().GetString("name")
		if name == "" {
			name = "Guest"
		}
		fmt.Printf("Hello, %s! Welcome to '''+self.name+r''' CLI.\n", name)
	},
}

// `math` command (parent command)
var mathCmd = &cobra.Command{
	Use:   "math",
	Short: "Perform mathematical operations",
	Long:  "This command allows you to perform simple math operations such as addition.",
}

// `math add` command
var addCmd = &cobra.Command{
	Use:   "add [num1] [num2]",
	Short: "Add two numbers",
	Long:  "This command takes two numbers as arguments and returns their sum.",
	Args:  cobra.ExactArgs(2), // Ensure exactly 2 arguments
	Run: func(cmd *cobra.Command, args []string) {
		num1, err1 := strconv.Atoi(args[0])
		num2, err2 := strconv.Atoi(args[1])

		if err1 != nil || err2 != nil {
			fmt.Println("Error: Please provide two valid numbers.")
			return
		}

		fmt.Printf("The sum of %d and %d is %d\n", num1, num2, num1+num2)
	},
}

// Initialize the CLI
func init() {
	// Add `greet` command
	rootCmd.AddCommand(greetCmd)

	// Add `math` command group
	rootCmd.AddCommand(mathCmd)
	mathCmd.AddCommand(addCmd)

	// Add a flag to `greet` command
	greetCmd.Flags().StringP("name", "n", "", "Your name")
}

// Entry point
func main() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
'''

        self.folders = [
          f'cli',
        #   f'gupy_apps/{self.name}/cli/dev/python_modules',
        #   f'gupy_apps/{self.name}/cli/dev/cython_modules',
          ]
        if self.lang == 'py':
            self.files = {
                f'cli/__init__.py': self.init_content,
                f'cli/__main__.py': self.main_content,
                f'cli/{self.name}.py': self.index_content,
                }
        else:
            self.files = {
                f'cli/main.go': self.main_content,
            }

    def create(self):
        import shutil
        # check if platform project already exists, if so, prompt the user
        if self.folders[0] in os.listdir('.'):
            while True:
                userselection = input(self.folders[0]+' already exists for the app '+ self.name +'. Would you like to overwrite the existing '+ self.folders[0]+' project? (y/n): ')
                if userselection.lower() == 'y':
                    click.echo(f'{Fore.YELLOW}Are you sure you want to recreate the '+ self.folders[0]+' project for '+ self.name +f'? (y/n){Style.RESET_ALL}')
                    userselection = input()
                    if userselection.lower() == 'y':
                        print("Removing old version of project...")
                        shutil.rmtree(os.path.join(os.getcwd(), self.folders[0]))
                        print("Continuing app platform creation.")
                        break
                    elif userselection.lower() != 'n':
                        click.echo(f'{Fore.RED}Invalid input, please type y or n then press enter...{Style.RESET_ALL}')
                        continue
                    else:
                        click.echo(f'{Fore.RED}Aborting app platform creation.{Style.RESET_ALL}')
                        return
                elif userselection.lower() != 'n':
                    click.echo(f'{Fore.RED}Invalid input, please type y or n then press enter...{Style.RESET_ALL}')
                    continue
                else:
                    click.echo(f'{Fore.RED}Aborting app platform creation.{Style.RESET_ALL}')
                    return
        
        for folder in self.folders:
            os.mkdir(folder)
            print(f'created "{folder}" folder.')
        
        for file in self.files:
            f = open(file, 'x')
            f.write(self.files.get(file))
            print(f'created "{file}" file.')
            f.close()

        if self.lang == 'py':
            # Get the directory of the current script
            current_directory = os.path.dirname(os.path.abspath(__file__))

            # Construct the path to the target file
            requirements_directory = os.path.join(os.path.dirname(current_directory), 'requirements.txt')       
            
            shutil.copy(requirements_directory, f'cli/requirements.txt')
        else:
            os.chdir('cli')
            os.system(f'go mod init {self.name}')
            os.system('go get -u github.com/spf13/cobra@latest')
            os.system('go get -u github.com/spf13/cobra/cobra@latest')

    def run(self):
        # detect os and make folder
        system = platform.system()

        if system == 'Darwin' or system == 'Linux':
            delim = '/'
        else:
            delim = '\\'
        if self.lang == 'py':
            # assign current python executable to use
            cmd = sys.executable.split(delim)[-1]

            # os.system(f'{cmd} {name}/desktop/dev/server/server.py')
            os.system(f'{cmd} {self.name}.py')
        else:
            os.system('go run main.go')




