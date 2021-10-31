import functools

import click
from appdirs import user_data_dir

from src.config import *
from src.error import AppError


class Utils:
    @property
    def session_dir(self) -> str:
        return user_data_dir(APP_NAME, APP_AUTHOR_ID)

    @staticmethod
    def error_wrapped(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AppError as e:
                click.echo(e.message, err=True)

        return wrapper
