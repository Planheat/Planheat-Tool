import zipfile
import json
import os
import pathlib


class ZipManager:

    FILE = "FILE"
    FOLDER = "FOLDER"
    OBJECT = "OBJECT"

    def __init__(self):
        self.file_dict = {}

    def add_file(self, source_type, source, relative_path: str):
        self.file_dict[relative_path] = {}
        self.file_dict[relative_path]["source"] = source
        self.file_dict[relative_path]["source_type"] = source_type

    def write(self, zip_file_path_name):
        with zipfile.ZipFile(zip_file_path_name, mode='w') as zf:
            for key in self.file_dict.keys():
                if self.file_dict[key]["source_type"] == self.FILE:
                    zf.write(self.file_dict[key]["source"],
                             arcname=key,
                             compress_type=zipfile.ZIP_DEFLATED)
                if self.file_dict[key]["source_type"] == self.OBJECT:
                    zf.writestr(key,
                                json.dumps(self.file_dict[key]["source"], indent=4),
                                compress_type=zipfile.ZIP_DEFLATED)
                if self.file_dict[key]["source_type"] == self.FOLDER:
                    for folderName, subfolders, filenames in os.walk(self.file_dict[key]["source"]):
                        for filename in filenames:
                            zf.write(os.path.join(folderName, filename),
                                     arcname=os.path.join(key, os.path.relpath(os.path.join(folderName, filename),
                                                                               start=self.file_dict[key]["source"])),
                                     compress_type=zipfile.ZIP_DEFLATED)

    def extract(self, zip_file_path, source_type, source, destination, trunc_base_path=0):
        with zipfile.ZipFile(zip_file_path, mode='r') as zf:
            if source_type == self.OBJECT:
                with zf.open(source) as my_file:
                    return json.load(my_file)
            if source_type == self.FILE:
                pass
            if source_type == self.FOLDER:
                for zip_info in zf.infolist():
                    if zip_info.filename[-1] == '/':
                        continue
                    file = zip_info.filename
                    if os.path.commonprefix([os.path.normpath(file), os.path.normpath(source)]) == os.path.normpath(
                            source):
                        new_filename = ""
                        for p in pathlib.Path(zip_info.filename).parts[trunc_base_path:]:
                            new_filename += p + "/"
                        zip_info.filename = new_filename[0:-1]
                        zf.extract(zip_info, os.path.normpath(destination))
                return os.path.normpath(os.path.join(destination, pathlib.Path(source).parts[trunc_base_path]))


