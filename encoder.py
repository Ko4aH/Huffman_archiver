from leaf import Leaf
BITS_IN_BYTE = 8


def encode(byte_stream: bytes):
    input_string = byte_stream.decode('utf-8')
    code_table = {}
    tree = prepare_tree(input_string)
    build_tree(tree)
    for symbol in tree:
        if len(symbol) == 1:
            code_table[symbol] = tree[symbol].code
    output_string = ''
    for char in input_string:
        output_string += code_table[char]
    leftover = BITS_IN_BYTE - len(output_string) % BITS_IN_BYTE
    output_string += '0' * leftover
    code_table['bits added'] = leftover
    output_byte_stream = translate_digits_to_bits(output_string)
    return output_byte_stream, code_table


def prepare_tree(input_string: str):
    tree = {}
    for symbol in input_string:
        if symbol in tree:
            tree[symbol].count += 1
        else:
            tree[symbol] = Leaf()
    return tree


def build_tree(tree: dict[str, Leaf]):
    number_of_unique_symbols = len(tree)
    while not all_leaves_are_used_in_tree(tree):
        symbol_with_min_count = find_symbol_with_min_count(tree)
        if len(symbol_with_min_count) == number_of_unique_symbols:
            if len(tree) == 1:
                tree[symbol_with_min_count].code = '0'
        else:
            another_symbol_with_min_count = find_symbol_with_min_count(tree)
            set_code_for_symbol(tree, symbol_with_min_count, '0')
            set_code_for_symbol(tree, another_symbol_with_min_count, '1')
            # Возможно, сработает неверно
            tree[symbol_with_min_count + another_symbol_with_min_count] = \
                Leaf(tree[symbol_with_min_count].count + tree[another_symbol_with_min_count].count)


def all_leaves_are_used_in_tree(tree: dict[str, Leaf]):
    all_leaves_are_used = True
    for symbol in tree:
        if not tree[symbol].is_used:
            all_leaves_are_used = False
            break
    return all_leaves_are_used


def find_symbol_with_min_count(tree: dict[str, Leaf]):
    min_count = float('inf')
    symbol_with_min_count = ''
    # Возможно, не заработает из-за перепутки leaf/symbol
    for symbol in tree:
        if not tree[symbol].is_used and tree[symbol].count < min_count:
            min_count = tree[symbol].count
            symbol_with_min_count = symbol
    tree[symbol_with_min_count].is_used = True
    return symbol_with_min_count


def set_code_for_symbol(tree: dict[str, Leaf], symbol: str, additional_bit: str):
    for (i, char) in enumerate(symbol):
        tree[symbol[i]].code = additional_bit + tree[symbol[i]].code


def translate_digits_to_bits(string: str):
    result = bytearray()
    for i in range(len(string)):
        # Потенциально долгая операция, можно делать struct.pack
        # Возможна ошибка синтаксиса to_bytes
        result += int(string[i:i + BITS_IN_BYTE], 2).to_bytes(1, 'big')
    return result


def decode(byte_stream: bytes, code_table: dict[str, str | int]):
    input_string = byte_stream.decode('utf-8')
    unpacked_string = translate_bits_to_digits(input_string)
    unpacked_string = unpacked_string[:-code_table['bits added']]
    return translate_string(unpacked_string, code_table)


def translate_bits_to_digits(string: str):
    result = ''
    for symbol in string:
        # Не проверено
        code = format(int.from_bytes(symbol, 'big'), 'b')
        # Возможна ошибка, написал по-новому
        significant_zeros = '0' * (BITS_IN_BYTE - len(code))
        code = significant_zeros + code
        result += code
    return result


def translate_string(string: str, code_table: dict[str, str | int]):
    # Нужна проверка на ошибку декодирования, уже есть в js
    # Возможна ошибка индексов
    count = 0
    result = ''
    while count < len(string):
        for symbol in code_table:
            if len(code_table[symbol]) > len(string) - count:
                continue
            if code_table[symbol] == string[count:count + len(code_table[symbol])]:
                result += symbol
                count += len(code_table[symbol])
                break
    return result
