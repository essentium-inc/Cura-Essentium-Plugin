import os
import zipfile


# https://stackoverflow.com/questions/31779392/exclude-a-directory-from-getting-zipped-using-zipfile-module-in-python
# handles zip file creation, with customizable filters
class Zipper:
    def __init__(self, source_path, destination_zip_path):
        self.source_path = source_path
        self.destination_zip_path = destination_zip_path

    @staticmethod
    def path_is_valid(path, ignore_dir, ignore_ext, ignore_file_names, ignore_file_name_contains):
        split_path = None

        if os.path.isfile(path):
            if ignore_ext:
                _, ext = os.path.splitext(path)
                if ext in ignore_ext:
                    return False

            file_name_with_ext = os.path.basename(path)

            if ignore_file_names:
                if file_name_with_ext in ignore_file_names:
                    return False

            if ignore_file_name_contains:
                for x in ignore_file_name_contains:
                    if x in file_name_with_ext:
                        return False

            split_path = os.path.dirname(path).split('\\/')
        else:
            if not ignore_dir:
                return True
            split_path = path.split('\\/')

        if ignore_dir:
            for s in split_path:
                if s in ignore_dir:  # You can also use set.intersection or [x for],
                    return False

        return True

    # recursive zip function
    def zip_it_good(self, path, root_dir, zf, ignore_dir=None, ignore_ext=None, ignore_file_names=None, ignore_file_name_contains=None):
        # zf is zipfile handle
        if os.path.isfile(path):
            if Zipper.path_is_valid(path, ignore_dir, ignore_ext, ignore_file_names, ignore_file_name_contains):
                relative = os.path.relpath(path, root_dir)
                zf.write(path, relative)
            return

        ls = os.listdir(path)
        for sub_file_or_dir in ls:
            if not Zipper.path_is_valid(sub_file_or_dir, ignore_dir, ignore_ext, ignore_file_names, ignore_file_name_contains):
                continue

            joined_path = os.path.join(path, sub_file_or_dir)
            self.zip_it_good(joined_path, root_dir, zf, ignore_dir, ignore_ext, ignore_file_names, ignore_file_name_contains)

    # zip function entry point, with options to ignore directories, extensions, and files
    def zip_it(self, ignore_dir=None, ignore_ext=None, ignore_file_names=None, ignore_file_name_contains=None, close_zip_file=False):
        # If you like to zip more files, just close_zip_file=False
        # and manually close the file or use "with xxx" on your own

        root_dir = self.source_path if os.path.isdir(self.source_path) else os.path.dirname(self.source_path)
        zip_file_obj = zipfile.ZipFile(self.destination_zip_path, "w")

        try:
            self.zip_it_good(self.source_path, root_dir, zip_file_obj, ignore_dir, ignore_ext, ignore_file_names, ignore_file_name_contains)
        finally:
            if close_zip_file:
                zip_file_obj.close()
