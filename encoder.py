from leaf import Leaf
from constants import *


def encode(byte_stream: bytes):
    code_table = {}
    tree = prepare_tree(byte_stream)
    build_tree(tree)
    for byte in tree:
        if len(byte) == 1:
            code_table[byte] = tree[byte].code
    output_string = ''
    for i in range(len(byte_stream)):
        byte = byte_stream[i:i + 1]
        output_string += code_table[byte]
    leftover = BITS_IN_BYTE - len(output_string) % BITS_IN_BYTE
    output_string += '0' * leftover
    code_table['bits added'] = leftover
    output_byte_stream = translate_digits_to_bits(output_string)
    return output_byte_stream, code_table


def prepare_tree(byte_stream: bytes):
    tree = {}
    for i in range(len(byte_stream)):
        byte = byte_stream[i:i + 1]
        if byte in tree:
            tree[byte].count += 1
        else:
            tree[byte] = Leaf()
    return tree


def build_tree(tree: dict[bytes, Leaf]):
    number_of_unique_symbols = len(tree)
    while not all_leaves_are_used_in_tree(tree):
        byte_with_min_count = find_byte_with_min_count(tree)
        if len(byte_with_min_count) == number_of_unique_symbols:
            if len(tree) == 1:
                tree[byte_with_min_count].code = '0'
        else:
            another_byte_with_min_count = find_byte_with_min_count(tree)
            set_code_for_byte(tree, byte_with_min_count, '0')
            set_code_for_byte(tree, another_byte_with_min_count, '1')
            tree[byte_with_min_count + another_byte_with_min_count] = \
                Leaf(
                    tree[byte_with_min_count].count +
                    tree[another_byte_with_min_count].count
                )


def all_leaves_are_used_in_tree(tree: dict[bytes, Leaf]):
    all_leaves_are_used = True
    for byte in tree:
        if not tree[byte].is_used:
            all_leaves_are_used = False
            break
    return all_leaves_are_used


def find_byte_with_min_count(tree: dict[bytes, Leaf]):
    min_count = float('inf')
    byte_with_min_count = bytearray()
    for byte in tree:
        if not tree[byte].is_used and tree[byte].count < min_count:
            min_count = tree[byte].count
            byte_with_min_count = byte
    tree[byte_with_min_count].is_used = True
    return bytes(byte_with_min_count)


def set_code_for_byte(tree: dict[bytes, Leaf],
                      byte_pack: bytes, additional_bit: str):
    for i in range(len(byte_pack)):
        byte = byte_pack[i:i + 1]
        tree[byte].code = additional_bit + tree[byte].code


def translate_digits_to_bits(string: str):
    result = bytearray()
    for i in range(0, len(string), 8):
        result += int(string[i:i + BITS_IN_BYTE], 2).to_bytes(1, 'big')
    return result


def decode(byte_stream: bytes, code_table: dict[str | bytes, str | int]):
    unpacked_string = translate_bits_to_digits(byte_stream)
    unpacked_string = unpacked_string[:-code_table['bits added']]
    return decode_string(unpacked_string, code_table)


def translate_bits_to_digits(byte_stream: bytes):
    result = ''
    for byte in byte_stream:
        code = format(byte, 'b')
        significant_zeros = '0' * (BITS_IN_BYTE - len(code))
        code = significant_zeros + code
        result += code
    return result


def decode_string(string: str, code_table: dict[str | bytes, str | int]):
    count = 0
    result = bytearray()
    while count < len(string):
        is_error = True
        for symbol in code_table:
            bits_for_symbol = len(code_table[symbol])
            if bits_for_symbol > len(string) - count:
                continue
            if code_table[symbol] == string[count:count + bits_for_symbol]:
                result += symbol
                count += bits_for_symbol
                is_error = False
                break
        if is_error:
            raise RuntimeError(FILE_IS_CORRUPTED_ERROR)
    return result
