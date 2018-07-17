from datetime import datetime
from multiprocessing.pool import ThreadPool

from .aur import find_aur_packages, get_all_aur_names
from .args import parse_args, PikaurArgs
from .core import spawn
from .pacman import get_pacman_command
from .pprint import bold_line


def _info_packages_thread_repo() -> str:
    args = parse_args()
    return spawn(get_pacman_command() + args.raw).stdout_text


def cli_info_packages(args: PikaurArgs) -> None:
    aur_pkg_names = args.positional or get_all_aur_names()
    with ThreadPool() as pool:
        aur_thread = pool.apply_async(find_aur_packages, (aur_pkg_names, ))
        repo_thread = pool.apply_async(_info_packages_thread_repo, ())
        pool.close()
        pool.join()
        repo_result = repo_thread.get()
        aur_result = aur_thread.get()

    if repo_result:
        print(repo_result, end='')

    aur_pkgs = aur_result[0]
    num_found = len(aur_pkgs)
    for i, aur_pkg in enumerate(aur_pkgs):
        pkg_info_lines = []
        for key, value in aur_pkg.__dict__.items():
            if key in ['firstsubmitted', 'lastmodified']:
                value = datetime.fromtimestamp(value).strftime('%c')
            elif isinstance(value, list):
                value = ', '.join(value)
            pkg_info_lines.append('{key:24}: {value}'.format(
                key=bold_line(key), value=value))
        print('\n'.join(pkg_info_lines) + ('\n' if i + 1 < num_found else ''))
