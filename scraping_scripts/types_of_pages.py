"""
Script to check what types of urls there are - will make easier to check if need to add '/text' or not
- event: needs '/text' at end of URL
- amendment: needs '/text' at end of URL
- bill: needs '/text' at end of URL
- committee-print: does not need '/text'
- congressional-record: does not need '/text'
- congressional-report: does not need '/text'
"""

import csv

input_file = 'congressional_to_go.csv'

url_types = set()

with open(input_file, encoding='utf-8') as infile:
    reader = csv.reader(infile)
    header = next(reader) # skip header row
    url_index = header.index("URL")

    row_count = 0
    for row in reader:
        url_parts = row[url_index].split('/')
        url_types.add(url_parts[3])
        row_count += 1

print(list(url_types))
print(row_count)

"""
Output:
['bill', 'amendment', 'event', 'committee-print', 'congressional-record', 'congressional-report']
12972

Double checked w/ ctrl+f:
    event: 2839
    bill: 645
    committee-print: 117
    congressional-record: 1625
    congressional-report: 433
    amendment: 7313
Total: 12972
"""
