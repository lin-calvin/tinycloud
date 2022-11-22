import pam
import os
import utils
from functools import lru_cache
import logging


class AuthPam:
    # pylint:disable=R0903
    def __init__(self):
        if os.uname().sysname == "Windows":
            raise RuntimeError("auth_pam only work on unix systems")
        if os.getuid() != 0:
            username = os.getlogin()
            logging.warning(
                'Run as a non-root user,pam will only work with user "{}"'.format(
                    username
                )
            )

    @lru_cache
    def do_auth(self, user, passwd):
        if user == "" or passwd == "":
            return False
        return pam.authenticate(user, passwd)


PROVIDE = {"auth": AuthPam}
