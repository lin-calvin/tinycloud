class auth:
    # pylint:disable=R0903
    def do_auth(self, _, __):
        return True


PROVIDE = {"auth": auth}
