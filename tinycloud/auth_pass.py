class auth:
    # pylint:disable=R0903
    def do_auth(_*):
        return True


PROVIDE = {"auth": auth}
