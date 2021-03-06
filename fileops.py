# jmelancon
# joseph@jmelancon.com
# 2022

'''handle most file-based operations for this program'''

import os
from pathlib import Path

import syscheck
from colors import colortext


def dir_sanitizer(directory):
    '''try to fix any input errors so we can use a user-provided directory'''

    # what if the directory input ends with a space? (drag and drop in kde)
    if directory[-1] == " ":
        directory = directory[:-1]

    # what if the directory is in apostraphes? (again, kde behavior with d&d)
    if directory[0] == "'" and directory[-1] == "'":
        directory = directory[1:-1]

    # what if the directory is in quotes? (just in case)
    if directory[0] == "\"" and directory[-1] == "\"":
        directory = directory[1:-1]

    #return cleansed dir
    return directory

def dir_exists_test(directory):
    '''test if a directory exists'''

    # clean up dir with the dir sanitizer
    parsed_dir = dir_sanitizer(directory)

    # return if the dir exists
    return os.path.isdir(parsed_dir)


def prep_dir_win(f_d, add_quotes):
    '''make win32 dir formatting work with the script'''
    split_dir = f_d.split("/")
    fixed_dir_array = []
    if add_quotes:
        for folder in split_dir:
            if " " in folder:
                new_folder = '"{}"'.format(folder)
                fixed_dir_array.append(new_folder)
            else:
                new_folder = folder
                fixed_dir_array.append(new_folder)
    else:
        fixed_dir_array = split_dir
    real_dir = "\\".join(fixed_dir_array)
    return real_dir


def find_files(music_dir, extensions):
    '''scan a provided directory for files. if a folder is found, recurse.'''
    music_dir = dir_sanitizer(music_dir) # fix any entry errors
    dir_array = os.listdir(music_dir)
        # uses listdir to get any files in that dir as an array
    file_array = []  # make an empty array for us to put full file paths in

    for each in dir_array:  # where the magic happens

        new_path = music_dir  # start with our base directory for the new path
        if new_path[-1] != "/":  # if there's no / at the end, fix it
            new_path += "/"  # boom
        new_path += each  # add our file or folder to new_path to get its path

        if os.path.isdir(new_path):  # if we have a folder, we must recurse.
            # print a simple status message
            file_array += find_files(new_path, extensions)  # recurse!

        else:  # if it's not a directory, then it must be a file!
            # lol this is awful. split the path at the periods
            get_extension_split = each.split(".")
            # check if we should put it on the list
            if get_extension_split[-1] in extensions:
                file_array.append(new_path)  # add it to our list of files.

    # return the array. if recursing, this is added to the parent's file_array.
    return file_array


def check_spaces(path):
    '''check if a directory has spaces'''
    has_space = False
    path_folders = path.split("/")
    for folder in path_folders:
        if " " in folder:
            has_space = True
    return has_space


def missing_dir_test(file_path):
    '''test if a dir exists from a file path. if it does not, make it!'''
    # start by splitting the path by slashes. this is not win32 compatable!
    split_file_dir = file_path.split("/")
    # chop off the last block of the array. this will be the file.
    split_file_dir.pop()
    # now, rejoin the array with slashes
    test_dir = "/".join(split_file_dir)
    # now we can create a Path object
    p = Path(test_dir)
    # if our path object doesn't exist, there is no real directory for what we
    # want. thus, we must make it!
    if not p.exists():
        # first, we tell the user it does not exist. this will be lost
        # in a sea of ffmpeg output, but i do not care.
        print(colortext("'{}' does not exist! creating now...".format(test_dir), "blue", style="i"))
        # on *nix systems, mkdir -p will recursively create directories.
        # this is good if, for example, the user uses window media player.
        # windows media player will put the music in an album folder that
        # is itself in an artist folder. this ensures that both the artist
        # and album folders are made.
        if syscheck.platform == "linux" or syscheck.platform == "unix":
            os.system('mkdir -p "{}"'.format(test_dir))
        # windows powershell also supports 'mkdir', but it recurses
        # by default, so if we include -p, it will make a directory called '-p'
        # windows also hates spaces :(
        # todo: add cmd.exe check
        elif syscheck.platform == "win32":
            os.system("mkdir {}".format(prep_dir_win(test_dir, True)))
        else:
            print(colortext("error, fileops.py broken :(", "white", "red"))
            exit()
