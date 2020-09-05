import datetime
import hashlib
import os
from pathlib import Path


def is_supported_type(file_path):
    supported_extensions = [
        ".jpg",
        ".jpeg",
        ".gif",
        ".png",
        ".mov",
        ".mpg",
        ".mpeg",
        ".m4v",
        ".mp4",
        ".avi",
        ".wmv",
        ".heic"
    ]

    file_extension = file_path.suffix
    return file_extension.lower() in supported_extensions


class FileInfo:
    def __init__(self, file_path):
        self.file_key = None
        self.file_hash = None
        self.file_path = file_path
        self.name = file_path.name
        self.file_stat = file_path.stat()
        self.size = self.file_stat.st_size
        creation_time = datetime.datetime.fromtimestamp(self.file_stat.st_ctime)
        modified_time = datetime.datetime.fromtimestamp(self.file_stat.st_mtime)
        self.created = creation_time if creation_time < modified_time else modified_time
        self.year = self.created.year
        self.month = self.created.month
        with open(self.file_path, "rb") as file_handle:
            self.file_hash = hashlib.md5(file_handle.read()).hexdigest()
        self.file_key = (self.size, self.file_hash)


class MediaSorter:
    def __init__(self, source_folder, destination_folder, test_mode=True):
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.test_mode = test_mode
        self.file_info_map = dict()
        self.error_files_map = dict()
        self.unsupported_files = list()
        self.duplicates = dict()
        self.move_errors = list()

        if not destination_folder.exists():
            print(f"Destination folder not found, creating: {destination_folder}")
            destination_folder.mkdir()

    def walk(self):
        for root, dirs, files in os.walk(str(self.source_folder), topdown=True):
            for name in files:
                file_path = Path(root) / name

                try:
                    if is_supported_type(file_path):
                        new_file = FileInfo(file_path)
                        if new_file.file_hash is None:
                            print(f"Invalid Hash: {file_path}")
                            self.error_files_map[file_path] = "Invalid Hash"
                        elif new_file.file_key in self.file_info_map.keys():
                            print(f"Found duplicate: {file_path}")
                            duplicate_file = self.file_info_map[new_file.file_key]
                            if new_file.file_key not in self.duplicates.keys():
                                self.duplicates[new_file.file_key] = set()
                                self.duplicates[new_file.file_key].add(str(duplicate_file.file_path))
                            self.duplicates[new_file.file_key].add(str(file_path))

                        else:
                            self.file_info_map[new_file.file_key] = new_file

                    else:
                        print(f"Unsupported file: {file_path}")
                        self.unsupported_files.append(file_path)

                except Exception as e:
                    print(f"ERROR: {file_path} - {str(e)}")
                    self.error_files_map[file_path] = e

    def report(self):
        current_report = {
            "valid_file_count": len(self.file_info_map.keys()),
            "duplicate_count": sum([len(dupe_list) - 1 for dupe_list in self.duplicates.values()]),
            "error_count": len(self.error_files_map.keys()),
            "unsupported_files_count": len(self.unsupported_files),
            "unsupported_extensions_found": list(set([file_path.suffix for file_path in self.unsupported_files])),
            "move_error_count": len(self.move_errors),
            "all_duplicates": [list(value) for value in self.duplicates.values()]
        }
        return current_report

    def move_all(self):
        for current_file in self.file_info_map.values():
            parent_folder = self.destination_folder / f"{current_file.year}-{current_file.month}"
            if not parent_folder.exists():
                parent_folder.mkdir()

            new_file_path = parent_folder / current_file.file_path.name
            counter = 0
            while new_file_path.exists():
                counter += 1
                prefix = current_file.file_path.stem
                suffix = current_file.file_path.suffix
                new_file_path = parent_folder / f"{prefix}({counter}){suffix}"

            try:
                if not self.test_mode:
                    current_file.file_path.rename(new_file_path)
                else:
                    print(f"Moving - {current_file.file_path} to {new_file_path}")
            except Exception as e:
                print(f"ERROR - could not move file - {current_file.file_path} - {str(e)}")
                self.move_errors.append(e)
