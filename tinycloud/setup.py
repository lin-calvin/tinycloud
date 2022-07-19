import sys
import os
import shutil
import argparse

src_dir=os.path.join(os.path.dirname(__file__),'conf/')

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config")
args = parser.parse_args()
if args.config:
    dir=args.config
else:
    dir='conf/'

#if not os.path.exists(dir):
 #   os.mkdir(dir)
shutil.copytree(src_dir,dir,dirs_exist_ok=True)

