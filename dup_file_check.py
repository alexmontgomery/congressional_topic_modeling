import os
import hashlib
from collections import defaultdict
import pandas as pd

def hash_file(path, block_size=65536):
    """Return the SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            hasher.update(block)
    return hasher.hexdigest()

def find_duplicate_files(directory):
    """Find and print duplicate files in a directory."""
    hashes = defaultdict(list)

    for root, _, files in os.walk(directory):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                file_hash = hash_file(file_path)
                hashes[file_hash].append(file_path)
            except Exception as e:
                print(f"Could not read file {file_path}: {e}")

    duplicates = {k: v for k, v in hashes.items() if len(v) > 1}
    
    if duplicates:
        global_count = 0
        df = pd.read_csv('congressional_to_go_withrows.csv')
        print("Duplicate files found:")
        for hash_val, files in duplicates.items():
            print(f"\nHash: {hash_val}")
            first_file = files[0]
            a = str(first_file).split('/')
            b = a[1].split('.')
            url = df[df['row_id'] == b[0]]['URL'].values[0]
            print(f"Sample URL from this set of duplicates: {url}")
            count = 0
            for file in files:
                print(f" - {file}")
                count += 1
                global_count += 1
            print(count)
        print(f"\nTotal count: {global_count}")
    else:
        print("No duplicate files found.")

# Example usage
directory_to_check = 'data'  # Change this to your target directory
find_duplicate_files(directory_to_check)
