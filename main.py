#!/usr/bin/env python
import os.path
import sys
import pickle
import encoder
import argparse
import file_worker
from constants import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', dest='output_file')
    input_file_name = sys.argv[1]
    for help_arg in HELPS:
        if help_arg in sys.argv:
            print(HELP_MESSAGE)
            sys.exit()

    if ('-d' in sys.argv and '-a' in sys.argv) or \
            ('-d' not in sys.argv and '-a' not in sys.argv):
        raise RuntimeError(SELECT_MODE_ERROR)

    if '-d' in sys.argv:
        count = sys.argv.index('-d')
        if len(sys.argv) < count + 2:
            raise RuntimeError(SPECIFY_DIR_ERROR)
        output_file_dir = sys.argv[count + 1]
        file_worker.decode_file(input_file_name, output_file_dir)
    else:
        output_file_name = ''
        output_path_is_specified = False
        count = sys.argv.index('-a')
        if len(sys.argv) >= count + 2:
            output_file_name = sys.argv[count + 1]
            output_path_is_specified = True
        file_worker.encode_file(input_file_name,
                                output_file_name,
                                output_path_is_specified)


if __name__ == '__main__':
    main()
