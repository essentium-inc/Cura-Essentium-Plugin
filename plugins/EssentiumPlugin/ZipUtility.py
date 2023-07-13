import os


# https://stackoverflow.com/questions/31779392/exclude-a-directory-from-getting-zipped-using-zipfile-module-in-python
class ZipUtility:
    @staticmethod
    def is_path_valid(path, ignore_dir, ignore_ext):
        split_text = None
        if os.path.isfile(path):
            if ignore_ext:
                _, ext = os.path.splitext(path)
                if ext in ignore_ext:
                    return False

            split_text = os.path.dirname(path).split('\\/')
        else:
            if not ignore_dir:
                return True
            split_text = path.split('\\/')

        if ignore_dir:
            for s in split_text:
                if s in ignore_dir:  # You can also use set.intersection or [x for],
                    return False

        return True

    @staticmethod
    def zip_dir_helper(path, root_dir, zf, ignore_dir=None, ignore_ext=None):
        # zf is zipfile handle
        if os.path.isfile(path):
            if ZipUtility.is_path_valid(path, ignore_dir, ignore_ext):
                relative = os.path.relpath(path, root_dir)
                zf.write(path, relative)
            return

        ls = os.listdir(path)
        for subFileOrDir in ls:
            if not ZipUtility.is_path_valid(subFileOrDir, ignore_dir, ignore_ext):
                continue

            joined_path = os.path.join(path, subFileOrDir)
            ZipUtility.zip_dir_helper(joined_path, root_dir, zf, ignore_dir, ignore_ext)

    @staticmethod
    def zip_dir(path, zf, ignore_dir=None, ignore_ext=None, close=False):
        root_dir = path if os.path.isdir(path) else os.path.dirname(path)

        try:
            ZipUtility.zip_dir_helper(path, root_dir, zf, ignore_dir, ignore_ext)
        finally:
            if close:
                zf.close()

