import pandas as pd
import re
import csv
import os
from lxml import etree


def extract_text_consolidated(html_file, xpath):
    try:
        with open(html_file, 'r', encoding='utf-8') as file:
            html_content = file.read()
        tree = etree.HTML(html_content)
        elements = tree.xpath(xpath)
        if elements:
            text = elements[0].text.strip() if elements[0].text else ""
            # Remove escape characters and replace excessive spaces with a single space
            clean_text = re.sub(r'[\n\r\t]', ' ', text)
            return " ".join(clean_text.split())
        else:
            return "No content found"
    except Exception as e:
        return f"Error: {e}"


# Update the CSV generation function to use the consolidated extraction
def process_files_consolidated_to_csv(input_files, output_csv, xpath):

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["File Name", "Extracted Text"])  # CSV header
        for file_path in os.listdir(input_files):
            print(file_path)
            file_path = os.path.join(input_files, file_path)
            file_name = os.path.basename(file_path)
            extracted_text = extract_text_consolidated(file_path, xpath)
            writer.writerow([file_name, extracted_text])

# Run the fully consolidated script
process_files_consolidated_to_csv('congressional_data', 'test.csv', '/html/body/div[2]/div/main/div[2]/div[2]/pre')


