import argparse
import json
import os
import sys
from pathlib import Path

import time

from media_sorter import MediaSorter


def get_options(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-s", "--source_path", help="Directory containing media", required=True)
    parser.add_argument("-d", "--destination_path", help="Directory to write media", required=True)
    parser.add_argument("-t", "--test_mode", help="Report preview of action, do not move files", action="store_true")
    options = parser.parse_args(args)
    return options


def main():
    command_params = get_options()
    print(command_params)
    source_path = Path(command_params.source_path)
    if not source_path.exists():
        print(f"Could not find directory {source_path}")
        exit(-1)

    destination_path = Path(command_params.destination_path)

    media_sorter = MediaSorter(source_path, destination_path, command_params.test_mode)
    print("Start walking folder structure")
    start_time = time.time()
    media_sorter.walk()
    walk_time = time.time() - start_time

    start_time = time.time()
    media_sorter.move_all()
    move_time = time.time() - start_time
    report = media_sorter.report()
    print(json.dumps(report, indent=2))
    print(f"walk_time={walk_time} move_time={move_time}")


if __name__ == "__main__":
    main()

