#!/usr/bin/env python
import os.path
import sys
import json
import encoder

SEGMENT_TO_ENCODE_SIZE = 1048576
FILE_IS_LAST_FIELD = 1
FILE_NAME_SIZE_FIELD = 1
ENCODED_FILE_SIZE_FIELD = 5
DATA_IN_SEGMENT_SIZE_FIELD = 3
CODE_TABLE_SIZE_FIELD = 3
HELP_MESSAGE = """
Данная программа позволяет архивировать файл при помощи кода Хаффмана.
Как пользоваться: 
python <имя программы> <файл для архивации или деархивации> [-d] [-o <директория для выходного файла>]
Используйте параметр -d для деархивации. Примеры использования:
python main.py input.txt
python main.py input.txt_archived -d
"""
# TODO: Надо добавить поддержку выбора директории для выходного файла


def main():
    file_name = sys.argv[1]
    if '-help' in sys.argv:
        print(HELP_MESSAGE)
    elif '-d' in sys.argv:
        decode_file(file_name)
    else:
        encode_file(file_name)


def encode_file(input_file_name: str):
    output_file_name = input_file_name + '_archived'
    byte_file_name = input_file_name.encode('utf-8')
    # На будущее, архивация нескольких файлов
    is_last_file = True

    with open(output_file_name, 'ab') as result:
        result.write(is_last_file.to_bytes(1, 'big'))
        result.write(len(byte_file_name).to_bytes(FILE_NAME_SIZE_FIELD, 'big'))
        result.write(byte_file_name)
        # Нужно будет добавить индекс начала следующего файла
        result.write(bytes(ENCODED_FILE_SIZE_FIELD))
        with open(input_file_name, 'rb') as input_file:
            # Надо написать условие: пока входной файл не закончился
            while True:
                segment_to_encode = input_file.read(SEGMENT_TO_ENCODE_SIZE)
                if not segment_to_encode:
                    break
                encoded_segment = encode_segment(segment_to_encode)
                result.write(encoded_segment)

    # Перезапись 5 байтов, нужно проверить, как оно работает
    with open(output_file_name, 'r+b') as result:
        next_file_start_index = os.stat(output_file_name).st_size
        result.seek(FILE_IS_LAST_FIELD + FILE_NAME_SIZE_FIELD + len(byte_file_name))
        result.write(next_file_start_index.to_bytes(ENCODED_FILE_SIZE_FIELD, 'big'))


def encode_segment(segment_to_encode: bytes):
    result = bytearray()
    output_byte_stream, code_table = encoder.encode(segment_to_encode)
    serialized_table = json.dumps(code_table).encode('utf-8')
    data_size = len(output_byte_stream)
    code_table_size = len(serialized_table)
    result += data_size.to_bytes(DATA_IN_SEGMENT_SIZE_FIELD, 'big')
    result += code_table_size.to_bytes(CODE_TABLE_SIZE_FIELD, 'big')
    result += output_byte_stream
    result += serialized_table
    return result


def decode_file(input_file_name: str):
    with open(input_file_name, 'rb') as f:
        # Добавить проверку, что файл последний
        is_last_file = bool.from_bytes(f.read(FILE_IS_LAST_FIELD), 'big')
        file_name_size = int.from_bytes(f.read(FILE_NAME_SIZE_FIELD), 'big')
        output_file_name = f.read(file_name_size).decode('utf-8')
        next_file_start_index = int.from_bytes(f.read(ENCODED_FILE_SIZE_FIELD), 'big')
        while f.tell() < next_file_start_index:
            data_size = int.from_bytes(f.read(DATA_IN_SEGMENT_SIZE_FIELD), 'big')
            code_table_size = int.from_bytes(f.read(CODE_TABLE_SIZE_FIELD), 'big')
            encoded_byte_stream = f.read(data_size)
            table_as_string = f.read(code_table_size).decode('utf-8')
            code_table = json.loads(table_as_string)
            decoded_data = encoder.decode(encoded_byte_stream, code_table)
            with open(output_file_name, 'ab') as result:
                result.write(decoded_data)


if __name__ == '__main__':
    main()
