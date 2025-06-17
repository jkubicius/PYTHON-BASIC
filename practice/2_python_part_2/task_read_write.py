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
        file.write(','.join(map(str, content))) # join list elements with ,

if __name__ == "__main__":

    folder = './files'

    files = [os.path.join(folder, filename) for filename in sorted(os.listdir(folder))]

    content = read_files(files)
    write_to_file("result.txt", content)
