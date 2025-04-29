import os
import hashlib
import shutil

"""
Go thru all files and only add to new duplicate-free directory if file has not been seen before
"""

def hash_file(path, block_size=65536):
    """Return the SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            hasher.update(block)
    return hasher.hexdigest()


def add_files(source, dest):

    hashes = set()

    for dirpath, dirnames, filenames in os.walk(source):
        for filename in filenames:
            src_path = os.path.join(dirpath, filename)

            # create a corresponding path in dest
            relative_path = os.path.relpath(dirpath, source)
            dest_dir = os.path.join(dest, relative_path)
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, filename)
            try:
                # get the current file's hash
                file_hash = hash_file(src_path)

                if file_hash not in hashes:
                    # if file hash not yet seen, add hash to set and copy file to destination directory
                    hashes.add(file_hash)
                    shutil.copy2(src_path, dest_path)

            except Exception as e:
                print(f"Could not read file {src_path}: {e}")


source = '../data'
dest = '../data_no_dups'
add_files(source, dest)
