import multiprocessing
from .config.args import parser
from ._targets import core_process

if __name__ == "__main__":
    # Process CLI arguments
    args = parser.parse_args()
    # Set the multiprocessing environment
    multiprocessing.set_start_method('spawn')
    # Begin the bot setup and initialisation
    login_lock = multiprocessing.Lock()
    new_core_process = multiprocessing.Process(target=core_process, args=(args, login_lock, None))
    new_core_process.start()
