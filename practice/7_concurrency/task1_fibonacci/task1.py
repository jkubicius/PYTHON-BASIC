import os
from random import randint
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import sys

# Allow printing very large Fibonacci numbers without hitting digit limit
sys.set_int_max_str_digits(100000)

OUTPUT_DIR = "./output"
RESULT_FILE = "./output/result.csv"


def fib(n: int):
    """Calculate a value in the Fibonacci sequence by ordinal number"""
    f0, f1 = 0, 1
    for _ in range(n-1):
        f0, f1 = f1, f0 + f1
    return f1

def func1(array: list):
    with ProcessPoolExecutor() as ex:
        results = ex.map(fib, array)
        for num, result in zip(array, results):
            with open(f"{OUTPUT_DIR}/temp/{num}.txt", "w") as f:
                f.write(str(result))

def open_files(filepath: str):
    with open(os.path.join(OUTPUT_DIR, "temp", filepath), "r") as f:
        return f.read()

def func2():
    files = os.listdir(f"{OUTPUT_DIR}/temp")
    data = []
    with ThreadPoolExecutor() as ex:
        tasks = {ex.submit(open_files, f): os.path.splitext(f)[0] for f in files}
        for task in as_completed(tasks):
            data.append((tasks[task], task.result()))

    with open(RESULT_FILE, "w") as f:
        for name, value in data:
            f.write(f"{name},{value}\n")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/temp", exist_ok=True)

    func1(array=[randint(1000, 100000) for _ in range(1000)])
    func2()