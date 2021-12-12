import os
import unittest
import main
from constants import *


class FileAfterUnzippingIsSame(unittest.TestCase):
    def test_if_output_path_is_not_specified(self):
        f = open(TEST_FILE, 'w')
        f.write('Hello, world!')
        f.close()
        self.assertTrue(SomeMethods.check_if_file_and_unzipped_are_same(TEST_FILE, False))

    def test_on_empty_file(self):
        empty_file = 'empty.tmp'
        with open(empty_file, 'w') as f:
            f.write('Hello, world!')
        self.assertTrue(SomeMethods.check_if_file_and_unzipped_are_same(empty_file))

    def test_on_text_file(self):
        text_file = 'text.txt'
        with open(text_file, 'w') as f:
            f.write('Hello, world!')
        self.assertTrue(SomeMethods.check_if_file_and_unzipped_are_same(text_file))

    def test_on_bin_file(self):
        bin_file = 'bytes.bin'
        f = open(bin_file, 'wb')
        f.write(b'Hello, world!')
        f.close()
        self.assertTrue(SomeMethods.check_if_file_and_unzipped_are_same(bin_file))


class IncorrectArguments(unittest.TestCase):

    def setUp(self) -> None:
        with open(TEST_FILE, 'w') as f:
            f.write('Hello, world!')

    def tearDown(self) -> None:
        os.remove(TEST_FILE)

    def test_large_output_file_name(self):
        large_name = 'large' * 100
        with self.assertRaises(RuntimeError):
            main.encode_file(TEST_FILE, large_name, True)

    def test_on_same_file_names(self):
        with self.assertRaises(RuntimeError):
            main.encode_file(TEST_FILE, TEST_FILE, True)

    def test_on_broken_archive(self):
        output_file = 'test_archive'
        decoded_dir = 'decoded'
        main.encode_file(TEST_FILE, output_file, True)
        with open(output_file, 'r+b') as f:
            middle_of_file = os.stat(output_file).st_size // 2
            f.seek(middle_of_file)
            f.write(b'some unexpected data')
        with self.assertRaises(RuntimeError):
            main.decode_file(output_file, decoded_dir)
        os.remove(output_file)
        file_dir, file_name = os.path.split(TEST_FILE)
        decoded_file = os.path.join(file_dir, decoded_dir, file_name)
        os.remove(decoded_file)


class OtherTests(unittest.TestCase):
    def test_if_archive_name_is_taken_write_in_another_file(self):
        archive_name = TEST_FILE + ARCHIVED_MARK
        data = 'Do not touch this data'
        with open(TEST_FILE, 'w') as f1:
            f1.write('Hello, world!')
        with open(archive_name, 'w') as f2:
            f2.write(data)
        main.encode_file(TEST_FILE, archive_name, False)
        with open(archive_name, 'r') as f2:
            check_data = f2.read()
            self.assertTrue(data == check_data)
        os.remove(TEST_FILE)
        os.remove(archive_name)
        os.remove('0_archived')


class SomeMethods:
    @staticmethod
    def files_are_equal(file: str, other_file: str):
        if os.stat(file).st_size != os.stat(other_file).st_size:
            return False
        with open(file) as f1, open(other_file) as f2:
            while True:
                block = f1.read(SEGMENT_TO_ENCODE_SIZE)
                other_block = f2.read(SEGMENT_TO_ENCODE_SIZE)
                if block != other_block:
                    return False
                if not block:
                    return True

    @staticmethod
    def check_if_file_and_unzipped_are_same(file: str, specify_output_archive=True):
        archived_file = file + ARCHIVED_MARK
        file_dir, file_name = os.path.split(file)
        dir_for_unarchived_file = os.path.join(file_dir, 'decoded')
        # subprocess.call(['python', 'main.py', file, '-a', archived_file])
        # subprocess.call(['python', 'main.py', archived_file, '-d', dir_for_unarchived_file])
        main.encode_file(file, archived_file, specify_output_archive)
        main.decode_file(archived_file, dir_for_unarchived_file)
        unarchived_file = os.path.join(dir_for_unarchived_file, file_name)
        result = SomeMethods.files_are_equal(file, unarchived_file)
        os.remove(file)
        os.remove(archived_file)
        os.remove(unarchived_file)
        return result


if __name__ == '__main__':
    unittest.main()
