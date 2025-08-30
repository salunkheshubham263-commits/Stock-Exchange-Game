import os

def scan_folder(path):
    for root, dirs, files in os.walk(path):
        print(f"Folder: {root}")
        for d in dirs:
            print(f"  Subfolder: {d}")
        for f in files:
            print(f"  File: {f}")

if __name__ == "__main__":
    scan_folder(r"c:\Users\Admin\Desktop\TeamWork\Stock-Exchange-Game")