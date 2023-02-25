import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import signal
from app import Tinycloud

DEF_CONFIG = ["~/.config/tinycloud", "conf", "/etc/tinycloud"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config")
    args = parser.parse_args()
    if args.config:
        conf_dir = args.config.replace("~", os.environ["HOME"])
    else:
        for i in DEF_CONFIG:
            if os.path.exists(i):
                conf_dir = i
                break
    if not os.path.exists(conf_dir):
        print(sys.argv[0] + ": " + conf_dir + ": No such file or directory")
        exit(255)
    tc = Tinycloud(conf_dir)

    def on_exit(*_):
        tc.exit()
        sys.exit()

    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, on_exit)
    print(
        "Server is run at http://{}:{}".format(
            tc.conf["http"]["addr"], tc.conf["http"]["port"]
        )
    )
    try:
        tc.run()    
    except KeyboardInterrupt:
        tc.exit()
        sys.exit()


def wsgi():
    if "~" not in os.environ and "~" in os.environ["TC_CONFIG_PATH"]:
        raise RuntimeError("$HOME hasn't be set")
    config_dir = os.environ["TC_CONFIG_PATH"].replace("~", os.environ["HOME"])
    return Tinycloud(config_dir)


if __name__ == "__main__":

    main()
