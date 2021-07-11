import os

class Directory:
    @staticmethod
    def exist(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
    @staticmethod
    def erase_file(file):
        with open(file, 'w'):
            pass