import os
from pathlib import Path

import time

if __name__ == "__main__":
    print("hello")

    source = Path(r"E:\GooglePhotoExtraction\Takeout\Google Photos")
    destination = Path(r"E:\destination")

    for root, dirs, files in os.walk(str(source), topdown=True):
        for name in files:
            file_path = Path(os.path.join(root, name))
            parent_name = file_path.parent.name
            parent_split = parent_name.split("-")
            if len(parent_split) == 3:
                new_parent_name = "{}-{}".format(parent_split[0], parent_split[1])
            else:
                new_parent_name = None

            if "json" not in str(file_path) and new_parent_name:
                file_destination = destination / new_parent_name / file_path.name
                print("path={} - parent_name = {}".format(file_path, parent_name))
                print("destination={}".format(file_destination))
                if not file_destination.parent.exists():
                    file_destination.parent.mkdir()

                if file_destination.exists():
                    new_name = "{}_{}".format(time.time(), file_destination.name)
                    file_destination = file_destination.parent / new_name

                file_path.rename(file_destination)
