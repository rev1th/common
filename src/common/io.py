
import os

def get_path(filename: str, folder: str = "data", format: str = None):
    if format:
        filename = f'{filename}.{format}'
    return os.path.join(folder, filename)
