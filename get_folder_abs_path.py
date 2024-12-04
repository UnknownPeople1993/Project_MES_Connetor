import os
import sys
class get_folder_abs_path():
    def __init__(self,relative_path):
        self.relative_path = relative_path

    def get_folder_abs_path(self,relative_path):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        config_folder = os.path.join(base_dir, relative_path)
        return os.path.abspath(config_folder)

