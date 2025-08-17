import subprocess
import pkgutil
import site
import sys
import logging
from importlib import metadata
from packaging.requirements import Requirement
from packaging.version import Version
from discord.ext.commands import errors
from .. import __title__
from . import CORE_EXTENSIONS

_log = logging.getLogger(__name__)


class DactylomancyExtensionNotFound(errors.ExtensionError):

    def __init__(self, message: str, extension: str, *args, name):
        self.extension = extension
        super().__init__(message, *args, name=name)


class DactylomancyDependencyNotMet(errors.ExtensionError):

    def __init__(self, message: str, extension: str, missing: list[str], late: list[str], *args, name):
        self.extension = extension
        self.missing = missing
        self.late = late
        super().__init__(message, *args, name=name)


def get_available_extensions() -> list[str]:
    available_extensions = []

    for module in pkgutil.iter_modules(path=site.getsitepackages()):
        if module.ispkg:
            try:
                dac_extensions = pkgutil.resolve_name(f'{module.name}:__dactylomancy__')
                for extension in dac_extensions:
                    available_extensions.append(f'{module.name}.{extension}')
            except AttributeError:
                pass

    return available_extensions


def validate_extensions(extensions: list[str]) -> None:
    available_extensions = get_available_extensions()

    proposed_extensions = CORE_EXTENSIONS.copy().extend(
        extensions
    )

    for i, extension in enumerate(proposed_extensions):
        if extension not in available_extensions:
            raise DactylomancyExtensionNotFound(f'Extension {extension} not found during search.', extension)
        else:
            try:
                dactylomancy_dependencies = pkgutil.resolve_name(f'{extension}:__dactylomancy_dependencies__')
                previous_extensions = proposed_extensions[:i]
                dependency_set = set(dactylomancy_dependencies)
                if not dependency_set.issubset(previous_extensions):
                    missing = dependency_set.difference(previous_extensions)
                    late = dependency_set.intersection(proposed_extensions[i:])
                    missing = missing.difference(late)
                    DactylomancyDependencyNotMet(
                        f'Extension {extension} does not have its dependenc(y/ies) not fulfilled.',
                        extension,
                        missing,
                        late,
                    )
            except AttributeError:
                pass


def get_installed_packages() -> dict[str, Version]:
    pip_result = subprocess.run(
        [sys.executable, '-m', 'pip', 'freeze'],
        capture_output=True,
        check=True,
    )

    result_dict = dict()
    for line in pip_result.stdout.decode('utf-8').splitlines():
        if '==' in line:
            package, version = line.split('==')
        elif ' @ ' in line:
            package, _ = line.split(' @ ')
            version = metadata.version(package)
        else:
            _log.warning(f'Could not parse pip freeze line:\n{line}')
        result_dict[package] = Version(version)

    return result_dict


def install_dependencies(dependencies: list[str], upgrade: bool = False) -> None:
    installed_packages = get_installed_packages()

    for dependency in dependencies:
        req = Requirement(dependency)
        if req.name not in installed_packages and (req.url or installed_packages[req.name] not in req.specifier):
            try:
                _log.info(f'Using pip to install: {dependency}.')
                command = [sys.executable, '-m', 'pip', 'install', dependency],
                if upgrade:
                    command.append('--upgrade')
                subprocess.run(
                    command,
                    capture_output=True,
                    check=True,
                )
            except subprocess.CalledProcessError as process_error:
                _log.warning(f'Error while running: {process_error.cmd}\n  stdout:\n{process_error.stdout}\n  stderr:\n{process_error.stderr}')
        else:
            _log.debug(f'Skipping over {dependency} as already fulfilled.')


def update_self() -> None:
    try:
        _log.info(f'Using pip to update: {__title__}.')
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', __title__, '-U'],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as process_error:
        _log.warning(f'Error while running: {process_error.cmd}\n  stdout:\n{process_error.stdout}\n  stderr:\n{process_error.stderr}')
