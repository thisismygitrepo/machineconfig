
"""Run cloud manager.
"""

from crocodile.cluster.loader_runner import CloudManager
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cloud", help="Rclone Config Name", type=str, default=None)

    args = parser.parse_args()
    cm = CloudManager(max_jobs=1, cloud=args.cloud)
    cm.run()


if __name__ == '__main__':
    main()
