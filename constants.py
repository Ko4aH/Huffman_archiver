SEGMENT_TO_ENCODE_SIZE = 1048576
BITS_IN_BYTE = 8
FILE_IS_LAST_FIELD = 1
FILE_NAME_SIZE_FIELD = 1
ENCODED_FILE_SIZE_FIELD = 5
DATA_IN_SEGMENT_SIZE_FIELD = 3
CODE_TABLE_SIZE_FIELD = 3

ARCHIVED_MARK = '_archived'
TOO_LONG_NAME_ERROR = 'Указано слишком длинное имя выходного файла'
FILE_NAME_IS_TAKEN_ERROR = """
Файл с именем выходного файла уже существует, укажите другое
"""
FILE_ALREADY_EXISTS_ERROR = """
Указанная папка уже содержит файл с таким же именем, укажите другую
"""
FILE_IS_CORRUPTED_ERROR = """
Файл повреждён и не может быть разархивирован
"""
SPECIFY_DIR_ERROR = """
Укажите папку для выходного файла
"""
SELECT_MODE_ERROR = """
Выберите один из режимов работы: архивация или деархивация, подробнее: -help
"""

HELP_MESSAGE = """
Данная программа позволяет архивировать файл при помощи кода Хаффмана.
Как пользоваться: 
python <имя программы> <файл для архивации или деархивации> 
[-d <путь>] [-a <путь>]
Параметры: 
-d - деархивация, после неё указывается папка для выходного файла;
-a - архивация, после неё указывается путь выходному файлу. 
Если не указать путь при архивации, 
то выходной файл будет иметь имя входного с окончанием "_archived".
Примеры использования:
python main.py input.txt -a
python main.py input.txt_archived -d folder
"""

HELPS = ['-help', '-h', '--help', '/?']

TEST_FILE = 'text.txt'
