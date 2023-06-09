import os
import glob
import shutil

def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)    
    return path


def clear_folder(path):
    shutil.rmtree(path)
    os.makedirs(path)


def copy_folder(source, dest):
    files = glob.glob(f'{source}/*')
    for f in files:
        shutil.copy(f, dest)


def copy_files(glob_pattern, dest):
    files = glob.glob(glob_pattern)
    for f in files:
        shutil.copy(f, dest)


def remove_files(glob_pattern):
    files = glob.glob(glob_pattern)
    for f in files:
        os.remove(f)


def rename_file(old, new):
    os.rename(old, new)


def get_files(glob_pattern):
    return glob.glob(glob_pattern)


def clear_folder_by_extention(path, extention):
    dir_name = path
    test = os.listdir(dir_name)

    if extention=="*":
        filelist = glob.glob(os.path.join(path, "*.*"))
        for f in filelist:
            os.remove(f)
    else:
        for item in test:
            if item.endswith(f'.{extention}'):
                os.remove(os.path.join(dir_name, item))
