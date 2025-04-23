"""Utility for colored console output."""

from typing import Optional


class Printer:
    """Handles colored console output formatting."""

    @staticmethod
    def print(content: str, color: Optional[str] = None):
        if hasattr(Printer, f"_print_{color}"):
            getattr(Printer, f"_print_{color}")(content)
        else:
            print(content)

    @staticmethod
    def _print_bold_purple(content):
        print("\033[1m\033[95m {}\033[00m".format(content))

    @staticmethod
    def _print_bold_green(content):
        print("\033[1m\033[92m {}\033[00m".format(content))

    @staticmethod
    def _print_purple(content):
        print("\033[95m {}\033[00m".format(content))

    @staticmethod
    def _print_red(content):
        print("\033[91m {}\033[00m".format(content))

    @staticmethod
    def _print_bold_blue(content):
        print("\033[1m\033[94m {}\033[00m".format(content))

    @staticmethod
    def _print_yellow(content):
        print("\033[93m {}\033[00m".format(content))

    @staticmethod
    def _print_bold_yellow(content):
        print("\033[1m\033[93m {}\033[00m".format(content))

    @staticmethod
    def _print_cyan(content):
        print("\033[96m {}\033[00m".format(content))

    @staticmethod
    def _print_bold_cyan(content):
        print("\033[1m\033[96m {}\033[00m".format(content))

    @staticmethod
    def _print_magenta(content):
        print("\033[35m {}\033[00m".format(content))

    @staticmethod
    def _print_bold_magenta(content):
        print("\033[1m\033[35m {}\033[00m".format(content))

    @staticmethod
    def _print_green(content):
        print("\033[32m {}\033[00m".format(content))
