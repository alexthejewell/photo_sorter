import hashlib
import os
from pathlib import Path

import time

import exifread as exifread


def get_date_taken(file_path):
    try:
        with open(str(file_path), 'rb') as fh:
            tags = exifread.process_file(fh, stop_tag="EXIF DateTimeOriginal")
            date_taken = tags["EXIF DateTimeOriginal"]
            return date_taken
    except:
        # print("Error file: {}".format(file_path))
        return None


def file_hash(file_path):
    hasher = hashlib.md5()
    with open(str(file_path), 'rb') as current_file:
        buf = current_file.read()
        hasher.update(buf)

    return hasher.hexdigest()


def move_file(source, destination, moved_count):
    print("{} From: {} To: {}".format(moved_count, file_path, new_location))


def delete_file(file_path):
    print("Deleting file: {}".format(file_path))


if __name__ == "__main__":
    source = Path(r"E:\Jewell Family Media\Photos")
    destination = Path(r"E:\Jewell Family Media")
    duplicates_folder = Path(r"E:\photo_duplicates")
    start_time = time.time()
    moved_file_count = 0
    duplicate_count = 0
    total_files = 0
    file_extensions = set()
    deleted_count = 0
    unhandled_count = 0
    video_count = 0

    for root, dirs, files in os.walk(str(source), topdown=True):
        root_path = Path(root)
        for name in files:
            total_files += 1
            file_path = root_path / name
            file_extensions.add(file_path.suffix)

            file_suffix = file_path.suffix

            if file_suffix in [".ini"]:
                deleted_count += 1
                delete_file(file_path)
            elif file_suffix in [".mpg", ".mpeg", ".avi", ".qt", ".mp4", ".m4v", ".wmv"]:
                print("Skipping video file: {}".format(file_path))
                video_count += 1
            else:
                date_taken = get_date_taken(file_path)
                if date_taken:
                    date_parts = date_taken.values.split(':')
                    date_folder = "{}-{}".format(date_parts[0], date_parts[1])
                    new_location = destination / date_folder / file_path.name
                    if new_location.exists():
                        if file_hash(file_path) == file_hash(new_location):
                            print("Ignoring duplicate")
                            duplicate_count += 1
                            new_location = duplicates_folder / "{}_{}".format(time.time(), name)
                            move_file(file_path, new_location, moved_file_count)
                        else:
                            new_location = new_location.parent / "{}_{}".format(time.time(), name)
                            print("Fixed name {}".format(new_location))
                            moved_file_count += 1
                            move_file(file_path, new_location, moved_file_count)
                    else:
                        move_file(file_path, new_location, moved_file_count)
                        moved_file_count += 1
                else:
                    print("Cannot process file: {}".format(file_path))
                    unhandled_count += 1

    print("Moved: {} files in {} minutes".format(moved_file_count, (time.time() - start_time)/60))
    print("Duplicate files {}".format(duplicate_count))
    print("File extensions encountered: {}".format(file_extensions))
    print("Deleted files: {}".format(deleted_count))
    print("Unhandled files: {}".format(unhandled_count))
    print("Video files: {}".format(video_count))
    print("Total: {}".format(total_files))
