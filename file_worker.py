#!/usr/bin/env python
import hashlib
import os.path
import sys
import pickle
import tkinter.filedialog

import encoder
from constants import *


def encode_file(input_file_name: str,
                output_file_name: str,
                output_path_is_specified: bool):
    if not output_path_is_specified:
        output_file_name = input_file_name + ARCHIVED_MARK
    output_file_name = check_file_path(output_file_name,
                                       output_path_is_specified)

    byte_file_name = input_file_name.encode('utf-8')
    is_last_file = True

    with open(output_file_name, 'ab') as result:
        result.write(is_last_file.to_bytes(1, 'big'))
        result.write(len(byte_file_name).to_bytes(FILE_NAME_SIZE_FIELD, 'big'))
        result.write(byte_file_name)
        result.write(bytes(ENCODED_FILE_SIZE_FIELD))
        with open(input_file_name, 'rb') as input_file:
            while True:
                segment_to_encode = input_file.read(SEGMENT_TO_ENCODE_SIZE)
                if not segment_to_encode:
                    break
                encoded_segment = encode_segment(segment_to_encode)
                result.write(encoded_segment)

    with open(output_file_name, 'r+b') as result:
        encoded_file_size = os.stat(output_file_name).st_size
        result.seek(FILE_IS_LAST_FIELD + FILE_NAME_SIZE_FIELD +
                    len(byte_file_name))
        result.write(
            encoded_file_size.to_bytes(ENCODED_FILE_SIZE_FIELD, 'big')
        )


def check_file_path(file_path: str, output_path_is_specified: bool):
    # Проверка на дубликат файла
    if os.path.exists(file_path):
        file_path = raise_error_or_set_new_name(file_path,
                                                output_path_is_specified,
                                                FILE_NAME_IS_TAKEN_ERROR)

    # Проверка на слишком длинное имя
    try:
        f = open(file_path, 'w')
        f.close()
        os.remove(file_path)
    except OSError:
        file_path = raise_error_or_set_new_name(file_path,
                                                output_path_is_specified,
                                                TOO_LONG_NAME_ERROR)
    return file_path


def raise_error_or_set_new_name(file_path: str,
                                output_path_is_specified: bool,
                                error_message: str):
    if output_path_is_specified:
        raise RuntimeError(error_message)
    else:
        count = 0
        while os.path.exists(file_path):
            directory, file = os.path.split(file_path)
            file = str(count) + ARCHIVED_MARK
            file_path = os.path.join(directory, file)
            count += 1
    return file_path


def encode_segment(segment_to_encode: bytes):
    result = bytearray()
    # hash_sum = hashlib.md5()
    # hash_sum.update(segment_to_encode)
    # result += hash_sum.digest_size.to_bytes(1, 'big')
    # result += hash_sum.digest()
    output_byte_stream, code_table = encoder.encode(segment_to_encode)
    serialized_table = pickle.dumps(code_table)
    data_size = len(output_byte_stream)
    code_table_size = len(serialized_table)
    result += data_size.to_bytes(DATA_IN_SEGMENT_SIZE_FIELD, 'big')
    result += code_table_size.to_bytes(CODE_TABLE_SIZE_FIELD, 'big')
    result += output_byte_stream
    result += serialized_table
    return result


def decode_file(input_file_name: str, output_file_dir: str):
    if not os.path.isdir(output_file_dir):
        os.makedirs(output_file_dir)
    with open(input_file_name, 'rb') as f:
        is_last_file = bool.from_bytes(f.read(FILE_IS_LAST_FIELD), 'big')
        file_name_size = int.from_bytes(f.read(FILE_NAME_SIZE_FIELD), 'big')
        output_file_name = f.read(file_name_size).decode('utf-8')
        encoded_file_size = int.from_bytes(
            f.read(ENCODED_FILE_SIZE_FIELD), 'big')
        output_path = os.path.join(output_file_dir, output_file_name)
        if os.path.exists(output_path):
            raise RuntimeError(FILE_ALREADY_EXISTS_ERROR)
        with open(output_path, 'ab') as result:
            while f.tell() < encoded_file_size:
                # hash_sum_size = int.from_bytes(
                #     f.read(1), 'big')
                # hash_sum = f.read(hash_sum_size)
                data_size = int.from_bytes(
                    f.read(DATA_IN_SEGMENT_SIZE_FIELD), 'big')
                code_table_size = int.from_bytes(
                    f.read(CODE_TABLE_SIZE_FIELD), 'big')
                encoded_byte_stream = f.read(data_size)
                code_table = bytearray()
                try:
                    code_table = pickle.loads(f.read(code_table_size))
                except:
                    raise RuntimeError(FILE_IS_CORRUPTED_ERROR)
                decoded_data = encoder.decode(encoded_byte_stream, code_table)
                # hash_of_decoded = get_hash_sum(decoded_data)
                # if hash_of_decoded != hash_sum:
                #     raise RuntimeError(FILE_IS_CORRUPTED_ERROR)
                result.write(decoded_data)


def get_hash_sum(segment: bytes):
    hash_sum = hashlib.md5()
    hash_sum.update(segment)
    return hash_sum.digest()
