
import discord
import discord.app_commands
from discord.utils import _shorten, _is_submodule, MISSING
from discord.app_commands.translator import locale_str
from discord.app_commands.commands import Command, ContextMenu, Group
from discord.app_commands.errors import (
    CommandAlreadyRegistered,
    CommandLimitReached,
)
from discord.abc import Snowflake
from discord.enums import AppCommandType
from discord.ext.commands import errors

import sys
import asyncio
import inspect
import importlib.util
import logging
import types
from typing import (
    TypeVar,
    Any,
    Tuple,
    Dict,
    List,
    Sequence,
    Optional,
    Union,
    Mapping,
    Coroutine,
    Callable,
)
from argparse import Namespace
from multiprocessing.synchronize import Lock as LockT

from .config.state import DactylomancyState
from . import __title__
from .utilities.embeds import ReferenceEmbed
from .utilities.parsing import TextMessageParser

DEFAULT_CONTEXTS = discord.app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True)
DEFAULT_INSTALLS = discord.app_commands.AppInstallationType(guild=False, user=True)
DEFAULT_INTENTS = discord.Intents.none()


class DactylomancyTree(discord.app_commands.CommandTree):

    def __init__(self, client: discord.Client, prefix: str):
        super().__init__(
            client,
            fallback_to_global=True,
            allowed_contexts=DEFAULT_CONTEXTS,
            allowed_installs=DEFAULT_INSTALLS,
        )
        self.prefix_group: Optional[Group] = None
        self._prefix(prefix)

    # Commands
    # This section draws heavily from discord.app_commands.tree at v2.5.2
    # Modified to enable addition to the root tree or the prefix group
    # Also removed the guild specific install functionality
    def add_command(
        self,
        command: Union[Command[Any, ..., Any], ContextMenu, Group],
        /,
        *,
        guild: Optional[Snowflake] = MISSING,
        guilds: Sequence[Snowflake] = MISSING,
        override: bool = False,
    ) -> None:
        if isinstance(command, ContextMenu):
            type = command.type.value
            name = command.name

            def _context_menu_add_helper(
                data: Dict[Tuple[str, Optional[int], int], ContextMenu],
                name: str = name,
                type: int = type,
            ) -> None:
                key = (name, None, type)
                found = key in self._context_menus
                if found and not override:
                    raise CommandAlreadyRegistered(name, None)

                # If the key is found and overridden then it shouldn't count as an extra addition
                # read as `0 if override and found else 1` if confusing
                to_add = not (override and found)
                total = sum(1 for _, g, t in self._context_menus if g is None and t == type)
                if total + to_add > 5:
                    raise CommandLimitReached(guild_id=None, limit=5, type=AppCommandType(type))
                data[key] = command
            _context_menu_add_helper(None, self._context_menus)
            return
        elif not isinstance(command, (Command, Group)):
            raise TypeError(f'Expected an application command, received {command.__class__.__name__} instead')

        # todo: validate application command groups having children (required)

        root = command.root_parent or command
        name = root.name

        found = name in self._global_commands
        if found and not override:
            print(self._global_commands)
            print(name)
            raise CommandAlreadyRegistered(name, None)

        to_add = not (override and found)
        if len(self._global_commands) + to_add > 100:
            raise CommandLimitReached(guild_id=None, limit=100)

        if self.prefix_group:
            self.prefix_group.add_command(command)
        else:
            self._global_commands[name] = root

    def command(
        self,
        *,
        name: Union[str, locale_str] = MISSING,
        description: Union[str, locale_str] = MISSING,
        nsfw: bool = False,
        guild: Optional[Snowflake] = MISSING,
        guilds: Sequence[Snowflake] = MISSING,
        auto_locale_strings: bool = True,
        extras: Dict[Any, Any] = MISSING,
    ):
        def decorator(func):
            if not inspect.iscoroutinefunction(func):
                raise TypeError('command function must be a coroutine function')

            if description is MISSING:
                if func.__doc__ is None:
                    desc = '…'
                else:
                    desc = _shorten(func.__doc__)
            else:
                desc = description

            command = Command(
                name=name if name is not MISSING else func.__name__,
                description=desc,
                callback=func,
                nsfw=nsfw,
                parent=None,
                auto_locale_strings=auto_locale_strings,
                extras=extras,
            )
            self.add_command(command)
            return command

        return decorator

    def context_menu(
        self,
        *,
        name: Union[str, locale_str] = MISSING,
        nsfw: bool = False,
        guild: Optional[Snowflake] = MISSING,
        guilds: Sequence[Snowflake] = MISSING,
        auto_locale_strings: bool = True,
        extras: Dict[Any, Any] = MISSING,
    ):
        def decorator(func) -> ContextMenu:
            if not inspect.iscoroutinefunction(func):
                raise TypeError('context menu function must be a coroutine function')

            actual_name = func.__name__.title() if name is MISSING else name
            context_menu = ContextMenu(
                name=actual_name,
                nsfw=nsfw,
                callback=func,
                auto_locale_strings=auto_locale_strings,
                extras=extras,
            )
            self.add_command(context_menu)
            return context_menu

        return decorator

    def _prefix(self, prefix: Optional[str] = None):
        if not self.prefix_group and prefix:
            self._create_prefix(prefix)
        elif prefix:
            self._modify_prefix(prefix)
        elif self.prefix_group:
            self._remove_prefix()

    def _create_prefix(self, prefix: str):
        logging.debug(f'Creating new prefix group for {prefix}.')

        # Clear existing commands from root
        existing_commands = self.get_commands(type=AppCommandType.chat_input)
        self.clear_commands(type=AppCommandType.chat_input, guild=None)

        new_prefix_group = discord.app_commands.Group(
            name=prefix,
            description=f'Prefix group for a {__title__} application.'
        )  # type: ignore[call-arg]

        self.add_command(new_prefix_group)
        self.prefix_group = new_prefix_group

        for command in existing_commands:
            command.parent = None
            self.prefix_group.add_command(command)

    def _modify_prefix(self, prefix: str):
        logging.debug(f'Modifying prefix group from {self.prefix_group.name} to {prefix}.')

        # Clear existing commands from root
        existing_commands = self.prefix_group.commands
        self.remove_command(self.prefix_group.name)

        new_prefix_group = discord.app_commands.Group(
            name=prefix,
            description=f'Prefix group for a {__title__} application.'
        )  # type: ignore[call-arg]

        self.prefix_group = None
        self.add_command(new_prefix_group)
        self.prefix_group = new_prefix_group

        for command in existing_commands:
            command.parent = None
            self.prefix_group.add_command(command)

    def _remove_prefix(self):
        logging.debug(f'Removing prefix group {self.prefix_group.name}.')

        # Clear existing commands from root
        existing_commands = self.prefix_group.commands
        self.remove_command(self.prefix_group.name)

        self.prefix_group = None

        for command in existing_commands:
            command.parent = None
            self.add_command(command)


# Type the listeners

T2 = TypeVar('T2')
Coro = Coroutine[Any, Any, T2]
CoroFunc = Callable[..., Coro[Any]]
CFT = TypeVar('CFT', bound='CoroFunc')


class DactylomancyBot(discord.Client):

    def __init__(
        self,
        config: DactylomancyState,
        args: Namespace,
        login_lock: LockT,
        followup_url: Optional[str] = None,
    ):
        super().__init__(intents=DEFAULT_INTENTS)
        self.config = config

        # Reboot prep
        self.login_lock = login_lock
        self._args = args
        self._followup_url = followup_url

        # Setup for listeners and extensions
        self.extra_events: Dict[str, List[CoroFunc]] = {}
        self.__tree = DactylomancyTree(self, self.config['core']['prefix'])  # type: ignore
        self.__extensions: Dict[str, types.ModuleType] = {}

        # Holding space for optional use by the presence and config command groups.
        self.public_group: Optional[Group] = None
        self.public_embed: Optional[discord.Embed] = None
        self.config_group: Optional[Group] = None
        self.config_embed: Optional[discord.Embed] = None
        # Holding space for optional use by the text parsers
        self.active_parsers: list[TextMessageParser] = []

    async def start(self, token):
        # Get the lock before logging in to ensure only one bot exists at a time.
        with self.login_lock:
            return await super().start(token, reconnect=True)

    # Listeners
    # This section draws heavily from discord.ext.commands.bot at v2.5.2

    def add_listener(self, func: CoroFunc, /, name: str = MISSING) -> None:
        name = func.__name__ if name is MISSING else name

        if not asyncio.iscoroutinefunction(func):
            raise TypeError('Listeners must be coroutines')

        if name in self.extra_events:
            self.extra_events[name].append(func)
        else:
            self.extra_events[name] = [func]

    def remove_listener(self, func: CoroFunc, /, name: str = MISSING) -> None:
        name = func.__name__ if name is MISSING else name

        if name in self.extra_events:
            try:
                self.extra_events[name].remove(func)
            except ValueError:
                pass

    def listen(self, name: str = MISSING) -> Callable[[CFT], CFT]:

        def decorator(func: CFT) -> CFT:
            self.add_listener(func, name)
            return func

        return decorator

    # Extensions
    # This section draws heavily from discord.ext.commands.bot at v2.5.2

    async def _remove_module_references(self, name: str) -> None:
        # remove all the listeners from the module
        for event_list in self.extra_events.copy().values():
            remove = []
            for index, event in enumerate(event_list):
                if event.__module__ is not None and _is_submodule(name, event.__module__):
                    remove.append(index)

            for index in reversed(remove):
                del event_list[index]

        # remove all relevant application commands from the tree
        self.__tree._remove_with_module(name)

    async def _call_module_finalizers(self, lib: types.ModuleType, key: str) -> None:
        try:
            func = getattr(lib, 'teardown')
        except AttributeError:
            pass
        else:
            try:
                await func(self)
            except Exception:
                pass
        finally:
            self.__extensions.pop(key, None)
            sys.modules.pop(key, None)
            name = lib.__name__
            for module in list(sys.modules.keys()):
                if _is_submodule(name, module):
                    del sys.modules[module]

    async def _load_from_module_spec(self, spec: importlib.machinery.ModuleSpec, key: str) -> None:
        # precondition: key not in self.__extensions
        lib = importlib.util.module_from_spec(spec)
        sys.modules[key] = lib
        try:
            spec.loader.exec_module(lib)  # type: ignore
        except Exception as e:
            del sys.modules[key]
            raise errors.ExtensionFailed(key, e) from e

        try:
            setup = getattr(lib, 'setup')
        except AttributeError:
            del sys.modules[key]
            raise errors.NoEntryPointError(key)

        try:
            await setup(self)
        except Exception as e:
            del sys.modules[key]
            await self._remove_module_references(lib.__name__)
            await self._call_module_finalizers(lib, key)
            raise errors.ExtensionFailed(key, e) from e
        else:
            self.__extensions[key] = lib

    def _resolve_name(self, name: str, package: Optional[str]) -> str:
        try:
            return importlib.util.resolve_name(name, package)
        except ImportError:
            raise errors.ExtensionNotFound(name)

    async def load_extension(self, name: str, *, package: Optional[str] = None) -> None:
        name = self._resolve_name(name, package)
        if name in self.__extensions:
            raise errors.ExtensionAlreadyLoaded(name)

        spec = importlib.util.find_spec(name)
        if spec is None:
            raise errors.ExtensionNotFound(name)

        await self._load_from_module_spec(spec, name)

    async def unload_extension(self, name: str, *, package: Optional[str] = None) -> None:
        name = self._resolve_name(name, package)
        lib = self.__extensions.get(name)
        if lib is None:
            raise errors.ExtensionNotLoaded(name)

        await self._remove_module_references(lib.__name__)
        await self._call_module_finalizers(lib, name)

    async def reload_extension(self, name: str, *, package: Optional[str] = None) -> None:
        name = self._resolve_name(name, package)
        lib = self.__extensions.get(name)
        if lib is None:
            raise errors.ExtensionNotLoaded(name)

        # get the previous module states from sys modules
        # fmt: off
        modules = {
            name: module
            for name, module in sys.modules.items()
            if _is_submodule(lib.__name__, name)
        }
        # fmt: on

        lib_table = self.config.get_table(name)

        try:
            # Unload and then load the module...
            await self._remove_module_references(lib.__name__)
            await self._call_module_finalizers(lib, name)
            await self.load_extension(name)
        except Exception:
            # if the load failed, the remnants should have been
            # cleaned from the load_extension function call
            # so let's load it from our old compiled library.
            await lib.setup(self, lib_table)
            self.__extensions[name] = lib

            # revert sys.modules back to normal and raise back to caller
            sys.modules.update(modules)
            raise

    async def setup_hook(self) -> None:
        # Sync commands if flag for it set
        if self.config['core']['sync_on_init']:
            logging.info('Syncing command tree on initialisation.')
            await self.tree.sync()
            self.config['core']['sync_on_init'] = False
            self.config.write_out()

        # Respond that updates are complete if returning from one
        if self._followup_url:
            if self.config_embed:
                embed_to_use = self.config_embed
            else:
                embed_to_use = ReferenceEmbed()

            webhook = discord.Webhook.from_url(
                self._followup_url,
                client=self
            )
            webhook.type = discord.WebhookType.application
            await webhook.send(
                embed=embed_to_use.get_simple_embed(
                    'Update and Restart',
                    'Complete.'
                ),
                ephemeral=True
            )
            self._followup_url = None

    async def load_extensions(self, override: Optional[Sequence[str]] = None) -> None:
        if override:
            extensions = override
        else:
            extensions = self.config['core']['extensions']

        for extension in extensions:
            logging.debug(f'Attempted to load extension: {extension}.')
            try:
                await self.load_extension(extension)
            except errors.ExtensionNotFound:
                logging.warning(f'Could not find extension: {extension}, check spelling and if a dependency is required.')
            except errors.ExtensionAlreadyLoaded:
                logging.warning(f'Found {extension} to already be loaded, check for duplication in your config.')
            except errors.NoEntryPointError:
                logging.warning(f'Found {extension} but it lacks a setup entry point, check if this is the intended import module.')

    async def reload_extensions(self) -> None:
        # TODO
        pass

    @property
    def extensions(self) -> Mapping[str, types.ModuleType]:
        return types.MappingProxyType(self.__extensions)

    @property
    def tree(self) -> DactylomancyTree:  # type: ignore
        return self.__tree

    def user_only(self):
        def predicate(interaction: discord.Interaction) -> bool:
            return interaction.user.id == self.config['core']['user']
        return discord.app_commands.check(predicate)

    def present_in_guild(self, guild_id) -> bool:
        return guild_id in self._connection._guilds
