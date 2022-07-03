import argparse
import os

from git import Repo

from Config import Config

parser = argparse.ArgumentParser()
parser.add_argument("-path", help="Path to config file that controls execution", type=str)
args = parser.parse_args()

config = Config(args.path)

Repo.clone_from(config.githubRepository, config.pathToModuleCode)

os.system('pip install -r {}/requirements.txt'.format(config.pathToModuleCode))