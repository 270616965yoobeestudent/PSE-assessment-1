import argparse
from typing import Callable


class HelpMessage(argparse.Action):
    def __init__(
        self,
        option_strings,
        dest=argparse.SUPPRESS,
        default=argparse.SUPPRESS,
        help=None,
        message: Callable[[argparse.ArgumentParser], str] | None = None,
    ):
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
        )
        self.message = message

    def __call__(self, parser, namespace, values, option_string=None):
        txt = self.message(parser) if self.message else parser.format_help()
        print(txt)
        parser.exit()
