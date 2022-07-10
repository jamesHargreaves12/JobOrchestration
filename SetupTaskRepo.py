import argparse
import os

from git import Repo,cmd

from Config import Config


def setupGit(config: Config):
    if os.path.exists(config.pathToModuleCode):
        localRepo = Repo(config.pathToModuleCode)
        localSha = localRepo.head.object.hexsha
        remoteSha = cmd.Git().ls_remote('https://github.com/jamesHargreaves12/SimpleML.git', heads=True)[:40]
        assert localSha == remoteSha
        return

    Repo.clone_from(config.githubRepository, config.pathToModuleCode)
    os.system('pip install -r {}/requirements.txt'.format(config.pathToModuleCode))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-path", help="Path to config file that controls execution", type=str)
    args = parser.parse_args()
    config = Config(args.path)
    setupGit(config)
