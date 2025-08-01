import argparse
import pathlib
from tomlkit.toml_file import TOMLFile
from .. import __title__
from .state import create_config_doc, validate_config_doc, DactylomancyState

parser = argparse.ArgumentParser(
    prog=f'{__title__}.config',
    description=f'a utility for creating, validating and sharing {__title__} configs',
)

subparsers = parser.add_subparsers(dest='sub_com')

create = subparsers.add_parser(
    'create',
    description='create a new config file'
)

create.add_argument(
    'filepath',
    help='path to save the config file if not the default ./config.toml',
    nargs='?',
    default='./config.toml',
    type=pathlib.Path,
    metavar='CONFIG_FILEPATH',
)

create.add_argument(
    '-t', '--token',
    help='a bot token to be inserted into the created config file',
    type=str,
)

create.add_argument(
    '-s', '--snowflake', '--id',
    help='a user id to be inserted into the created config file',
    type=int,
)

validate = subparsers.add_parser(
    'validate',
    description='validate an existing config file'
)

validate.add_argument(
    'filepath',
    help='path to the config file if not the default ./config.toml',
    nargs='?',
    default='./config.toml',
    type=pathlib.Path,
    metavar='CONFIG_FILEPATH',
)

sanitise = subparsers.add_parser(
    'sanitise',
    description='sanitise an existing config file to produce a sharable version'
)

sanitise.add_argument(
    'filepath',
    help='path to a config file if not the default ./config.toml',
    nargs='?',
    default='./config.toml',
    type=pathlib.Path,
    metavar='SOURCE_CONFIG_FILEPATH',
)

sanitise.add_argument(
    'output_filepath',
    help='path to a config file if not the default ./sanitised_config.toml',
    nargs='?',
    default='./sanitised_config.toml',
    type=pathlib.Path,
    metavar='OUTPUT_CONFIG_FILEPATH',
)


def standalone_utility():
    args = parser.parse_args()
    t_file = TOMLFile(args.filepath)
    if args.sub_com == 'create':
        t_doc = create_config_doc(args.token, args.snowflake)
        t_file.write(t_doc)
    elif args.sub_com == 'validate':
        t_doc = t_file.read()
        validate_config_doc(t_doc)
    elif args.sub_com == 'sanitise':
        out_file = TOMLFile(args.output_filepath)
        d_state = DactylomancyState(t_file, t_file.read())
        out_file.write(d_state.get_sanitised_doc())
