import argparse
import pathlib
import os
from .. import __title__, __version__

parser = argparse.ArgumentParser(
    prog=__title__,
    description='a tool for allowing a voice its own presence on discord, requires a discord app, and attached bot, to operate',
    epilog='for additional support, begin at https://aksan.dev/dactylomancy/'
)

parser.add_argument(
    'token',
    help='bot token acquired from https://discord.com/developers/applications for the indended application, only needed during initial setup or due to a token update',
    type=str,
    nargs='?',
    default=os.getenv('DACTYLOMANCY_TOKEN'),
    metavar='TOKEN',
)

parser.add_argument(
    'id',
    help='user-id acquired from inside discord for the intented user, only needed during initial setup or due to a change in user account',
    type=str,
    nargs='?',
    default=os.getenv('DACTYLOMANCY_USER_ID'),
    metavar='USER-ID',
)

parser.add_argument(
    '-v', '--version',
    help='print version information and exit',
    action='version',
    version=f'{parser.prog} {__version__}'
)

parser.add_argument(
    '-c', '--config',
    help='path to a config file if not the default ./config.toml',
    default=os.getenv('DACTYLOMANCY_CONFIG_FILEPATH', './config.toml'),
    type=pathlib.Path,
    metavar='CONFIG_FILEPATH',
)

parser.add_argument(
    '-l', '--logging',
    help='path to a logging file if not the default dactylomancy.log',
    default=os.getenv('DACTYLOMANCY_LOGGING_FILEPATH', './dactylomancy.log'),
    type=pathlib.Path,
    metavar='LOGGING_FILEPATH',
)

parser.add_argument(
    '-p', '--print',
    help='additionally print logged information to stderr',
    action='store_true',
)

parser.add_argument(
    '-d', '--detail',
    help='sets the level of detail for the logging, default to INFO',
    default='INFO',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
)

parser.add_argument(
    '-s', '--sync',
    help='instructs the bot to sync commands on ready during this initialisation',
    action='store_true',
)
