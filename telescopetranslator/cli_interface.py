import os
import sys
import importlib
import traceback
import configparser
from pathlib import Path
from argparse import ArgumentParser, ArgumentError
from typing import Dict, List, Tuple
import logging
from datetime import datetime, timedelta

import yaml

from ddoitranslatormodule.ddoiexceptions.DDOIExceptions import DDOITranslatorModuleNotFoundException
from ddoitranslatormodule.BaseFunction import TranslatorModuleFunction


class LinkingTable():
    """Class storing the contents of a linking table
    """

    def __init__(self, filename):
        """Create the LinkingTable

        Parameters
        ----------
        filename : str
            Filepath to the linking table
        """
        try:
            with open(filename) as f:
                self.cfg = yaml.load(f, Loader=yaml.FullLoader)
        except:
            print(f"Unable to load {filename}")
            return

        self.prefix = self.cfg['common']['prefix']
        self.suffix = self.cfg['common']['suffix']
        self.links = self.cfg['links']

    def get_entry_points(self) -> List[str]:
        """Gets a list of all the entry points listed in the linking table

        Returns
        -------
        List[str]
            List of all entry points (keys) in the linking table
        """
        eps = [key for key in self.links]
        return eps

    def print_entry_points(self, prefix="") -> None:
        """Prints out all the entry points listed in the linking table

        Parameters
        ----------
        prefix : str, optional
            String to be prepended to each line, by default ""
        """
        for i in self.get_entry_points():
            print(prefix + i)

    def get_link(self, entry_point) -> str:
        """Gets the full import string from the linking table for a given entry
        point (key)

        Parameters
        ----------
        entry_point : str
            Entry point (key) to get

        Returns
        -------
        str
            Python import string for the requested function

        Raises
        ------
        KeyError
            Raised if the linking table does not have an entry matching entry_point
        """
        if entry_point not in self.links:
            raise KeyError(f"Failed to find {entry_point} in table")
        output = ""
        if self.prefix:
            output += self.prefix + "."
        output += self.links[entry_point]["cmd"]
        if self.suffix:
            output += "." + self.suffix
        return output

    def get_link_and_args(self, entry_point) -> Tuple[str, list]:
        """Gets both an import string for an entry point, and a list of Tuples 
        containing information about default arguments needed

        Parameters
        ----------
        entry_point : str
            Key in the links section in the linking table being searched for

        Returns
        -------
        Tuple[str, list]
            Import string for the entry point, and a list of tuples where the first
            item is the argument that must be inserted, and the second is the index
            where it should go
        """
        link = self.get_link(entry_point)
        args = None
        # Load the config file, and create an array with [None, SADSASD, None, etc...]
        # maybe return a function that takes in a partial arguments array and outputs a full array?
        args = []
        if 'args' in self.links[entry_point].keys():
            for arg in self.links[entry_point]['args']:
                arg_index = arg.split("_")[1]
                args.append(
                    (int(arg_index), self.links[entry_point]['args'][arg]))
                # Loop over these tuples and insert them into the execution args
                # i.e. args.insert(idx = tup[0], arg=tup[1])
        return link, args


def get_linked_function(linking_tbl, key) -> Tuple[TranslatorModuleFunction, str]:
    """Searches a linking table for a given key, and attempts to fetch the
    associated python module

    Parameters
    ----------
    linking_tbl : LinkingTable
        Linking Table that should be searched
    key : str
        CLI function being searched for

    Returns
    -------
    Tuple[class, str]
        The class matching the given key, and the module path string needed to
        import it. If no such module is found, returns (None, None)

    Raises
    ------
    DDOITranslatorModuleNotFoundException
        If there is not an associated Translator Module
    """

    # Check to see if there is an entry matching the given key
    if key not in linking_tbl.get_entry_points():
        raise DDOITranslatorModuleNotFoundException(
            f"Unable to find an import for {key}")
    link, default_args = linking_tbl.get_link_and_args(key)

    # Get only the module path
    link_elements = link.split(".")
    # Get only the module import string
    module_str = ".".join(link_elements[:-1])
    # Get only the class name
    class_str = link_elements[-1]

    try:
        # Try to import the package from the string in the linking table
        mod = importlib.import_module(module_str)

        try:
            return getattr(mod, class_str), default_args, link
        except:
            print("Failed to find a class with a perform method")
            return None, None, None

    except ImportError as e:
        print(f"Failed to import {module_str}")
        print(traceback.format_exc())
        return None, None, None

def create_logger():
    log = logging.getLogger('cli_interface')
    log.setLevel(logging.DEBUG)
    ## Set up console output
    LogConsoleHandler = logging.StreamHandler()
    LogConsoleHandler.setLevel(logging.INFO)
    LogFormat = logging.Formatter('%(asctime)s:%(filename)s:%(levelname)8s: %(message)s')
    LogConsoleHandler.setFormatter(LogFormat)
    log.addHandler(LogConsoleHandler)
    ## Set up file output
    utnow = datetime.utcnow()
    date = utnow-timedelta(days=1)
    date_str = date.strftime('%Y%b%d').lower()
    logdir = Path(f"/s/sdata1701/{os.getlogin()}/{date_str}/logs")
    if logdir.exists() is False:
        logdir.mkdir(parents=True)
    LogFileName = logdir / 'cli_interface.log'
    LogFileHandler = logging.FileHandler(LogFileName)
    LogFileHandler.setLevel(logging.DEBUG)
    LogFileHandler.setFormatter(LogFormat)
    log.addHandler(LogFileHandler)
    return log

def main():

    #
    # Logging
    #

    logger = create_logger()
    logger.debug("Created logger")
    invocation = ' '.join(sys.argv)
    logger.debug(f"Invocation: {invocation}")

    #
    # Build the linking table
    #

    table_loc = Path(__file__).parent / "linking_table.yml"
    if not table_loc.exists():
        logger.error(f"Failed to find a linking table at {str(table_loc)}")
        logger.error("Exiting...")
        sys.exit(1)
    linking_tbl = LinkingTable(table_loc)

    #
    # Handle command line arguments
    #

    cli_parser = ArgumentParser(add_help=False, conflict_handler="resolve")
    cli_parser.add_argument("-l", "--list", dest="list", action="store_true", help="List functions in this module")
    cli_parser.add_argument("-n", "--dry-run", dest="dry_run", action="store_true", help="Print what function would be called with what arguments, with no actual invocation")
    cli_parser.add_argument("-h", "--help", dest="help", action="store_true")
    cli_parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Print extra information")
    cli_parser.add_argument("-f", "--file", dest="file", help="JSON or YAML OB file to add to arguments")
    # cli_parser.add_argument("function_args", nargs="*", help="Function to be executed, and any needed arguments")
    logger.debug("Parsing cli_interface.py arguments...")
    parsed_args, function_args = cli_parser.parse_known_args()
    logger.debug("Parsed.")

    # Help:
    if parsed_args.help:
        logger.debug("Printing help...")
        # If this is help for a specific module:
        if len(function_args):
            try:
                function, preset_args, mod_str = get_linked_function(
                    linking_tbl, function_args[0])
                func_parser = ArgumentParser(add_help=False)
                func_parser = function.add_cmdline_args(func_parser)
                func_parser.print_help()
                if parsed_args.verbose:
                    print(function.__doc__)
                if preset_args and len(preset_args) > 0:
                    print("Preset arguments:")
                    print(preset_args)
                # figure out how to access the argparse from outside, and print the -h
            except DDOITranslatorModuleNotFoundException as e:
                print(e)
                print("Available options are:")
                linking_tbl.print_entry_points("   ")
        # Print help for using this CLI script
        else:
            cli_parser.print_help()
        return
    # List:
    if parsed_args.list:
        logger.debug("Printing list...")
        linking_tbl.print_entry_points()
        return

    #
    # Handle Execution
    #

    try:

        # Get the function
        logger.debug(f"Fetching {function_args[0]}...")
        function, args, mod_str = get_linked_function(
            linking_tbl, function_args[0])
        logger.debug(f"Found at {mod_str}")

        # Insert required default arguments
        logger.debug(f"Inserting default arguments")
        final_args = function_args[1:]
        for arg_tup in args:
            final_args.insert(arg_tup[0], str(arg_tup[1]))

        # Build an ArgumentParser and attach the function's arguments
        parser = ArgumentParser(add_help=False)
        logger.debug(f"Adding CLI args to parser")
        parser = function.add_cmdline_args(parser)
        logger.debug("Parsing function arguments...")
        try:
            parsed_func_args = parser.parse_args(final_args)
            logger.debug("Parsed.")
        except ArgumentError as e:
            logger.error("Failed to parse arguments!")
            logger.error(e)
            print(e)
            sys.exit(1)
            
        """
        if parsed_args.file:
            logger.warn("File functionality is untested. Use at your own risk")
            logger.info(f"Found an input file: {parsed_args.file}")
            # There is a JSON or YAML file that needs reading!
            # Read it, based on file extension
            if [".yml", ".yaml"] in parsed_args.file:
                import yaml
                with open(parsed_args.file, "r") as stream:
                    try:
                        OB = yaml.safe_load(stream)
                        parsed_func_args['OB'] = OB
                    except yaml.YAMLError as e:
                        logger.error(f"Failed to load {parsed_args.file}")
                        logger.error(e)
                        return
            elif [".json"] in parsed_args.file:
                import json
                with open(parsed_args.file, "r") as stream:
                    try:
                        OB = json.load(stream)
                        parsed_func_args['OB'] = OB
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to load {parsed_args.file}")
                        logger.error(e)
                        return
                    
            else:
                logger.error(
                    "Filetype is not supported. I understand [.yaml, .yml, .json]")
                return
        """
        if parsed_args.dry_run:
            logger.info("Dry run:")
            logger.info(f"Function: {mod_str}\nArgs: {' '.join(final_args)}")

        else:
            if parsed_args.verbose:
                print(f"Executing {mod_str} {' '.join(final_args)}")
            logger.debug(f"Executing {mod_str} {' '.join(final_args)}")
            function.execute(parsed_func_args, logger=logger)

    except DDOITranslatorModuleNotFoundException as e:
        logger.error("Failed to find Translator Module")
        logger.error(e)
        sys.exit(1)
    except ImportError as e:
        logger.error("Found translator module, but failed to import it")
        logger.error(e)
        sys.exit(1)
    except TypeError as e:
        logger.error(traceback.format_exc())
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected exception encountered in CLI:")
        logger.error(e)
        sys.exit(1)
    
    # Not strictly needed, but it's nice to be explicit
    sys.exit(0)


if __name__ == "__main__":
    main()
