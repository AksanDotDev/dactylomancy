import asyncio
import logging
import multiprocessing
from argparse import Namespace
from typing import Optional
from multiprocessing.synchronize import Lock as LockT
from .bot import DactylomancyBot
from .config.args import parser
from .config.logging import setup_logging
from .config.state import initialise_config_state
from .extensions.loading import install_dependencies, update_self


def launch_process():
    # Process CLI arguments
    args = parser.parse_args()
    # Set the multiprocessing environment
    multiprocessing.set_start_method('spawn')
    # Begin the bot setup and initialisation
    login_lock = multiprocessing.Lock()
    new_core_process = multiprocessing.Process(target=core_process, args=(args, login_lock, None))
    new_core_process.start()


def core_process(
    args: Namespace,
    login_lock: LockT,
    followup_url: Optional[str] = None,
):

    setup_logging(args.detail, args.logging, args.print)
    logging.info('Initializing configuration.')
    state = initialise_config_state(args.config, args.token, args.id)

    install_dependencies(state)

    if args.sync:
        state['core']['sync_on_init'] = True
        args.sync = False

    logging.info('Creating bot.')
    bot = DactylomancyBot(state, args, login_lock, followup_url)
    logging.info('Running initialisation.')
    asyncio.run(core_async_loop(bot))


async def core_async_loop(bot: DactylomancyBot):
    # Any async initialisation should go here

    # Begin the bot proper
    async with bot:
        # Load the initial extensions
        await bot.load_extensions()
        # Acquire the login_lock
        await bot.start(bot.config['core']['token'])


def update_process(
    args: Namespace,
    login_lock: LockT,
    followup_url: str,
):

    setup_logging(args.detail, args.logging, args.print)
    logging.info('Beginning update process.')

    with login_lock:  # Use to prevent attempts to update while the bot it logged in
        print('This is where I would run self update, IF I HAD ANY!!!')
        update_self()

    logging.info('Relaunching core process.')
    new_core_process = multiprocessing.Process(
        target=core_process,
        args=(
            args,
            login_lock,
            followup_url,
        )
    )
    new_core_process.start()
