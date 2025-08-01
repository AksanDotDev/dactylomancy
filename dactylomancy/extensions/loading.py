import subprocess
import sys
import logging
from packaging.requirements import Requirement
from packaging.version import Version
from ..config.state import DactylomancyState
from .. import __title__


def get_installed_packages() -> dict[str, Version]:
    pip_result = subprocess.run(
        [sys.executable, '-m', 'pip', 'freeze'],
        capture_output=True,
        check=True,
    )
    result_dict = dict()
    for package, version in map(lambda x: x.split('=='), pip_result.stdout.decode('utf-8').splitlines()):
        result_dict[package] = Version(version)
    return result_dict


def install_dependencies(state: DactylomancyState) -> None:
    installed_packages = get_installed_packages()

    for dependency in state['core']['dependencies']:
        req = Requirement(dependency)
        if req.name not in installed_packages and (req.url or installed_packages[req.name] not in req.specifier):
            try:
                logging.info(f'Using pip to install: {dependency}.')
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', dependency],
                    capture_output=True,
                    check=True,
                )
            except subprocess.CalledProcessError as process_error:
                logging.warning(f'Error while running: {process_error.cmd}\n  stdout:\n{process_error.stdout}\n  stderr:\n{process_error.stderr}')
        else:
            logging.debug(f'Skipping over {dependency} as already fulfilled.')


def update_self() -> None:
    try:
        logging.info(f'Using pip to update: {__title__}.')
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', __title__, '-U'],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as process_error:
        logging.warning(f'Error while running: {process_error.cmd}\n  stdout:\n{process_error.stdout}\n  stderr:\n{process_error.stderr}')
