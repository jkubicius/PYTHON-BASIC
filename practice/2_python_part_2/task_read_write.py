"""
Read files from ./files and extract values from them.
Write one file with all values separated by commas.

Example:
    Input:

    file_1.txt (content: "80")
    file_2.txt (content: "37")
    file_3.txt (content: "15")

    Output:

    result.txt(content: "80, 37, 15")
"""
import os


def read_files(file_paths: list[str]):
    result = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r') as content:
                result.append(content.read())
        except FileNotFoundError:
            print(f"Missing file: {file_path}")
    return result

def write_to_file(filename: str, content: list[str]):
    with open(filename, 'w') as file:
        file.write(', '.join(content)) # join list elements with ,

def get_number(filename: str):
    return int(filename.split('_')[1].split('.')[0]) # extract number from filename

if __name__ == "__main__":

    folder = './files'

    files = sorted(os.listdir(folder), key=get_number)
    files = [os.path.join(folder, filename) for filename in files]

    content = read_files(files)
    write_to_file("result.txt", content)