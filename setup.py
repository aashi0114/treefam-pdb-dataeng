import os

# creating the treefam-pdb and checking whether it already exists
if not os.path.isdir('treefam-pdb'):
    os.mkdir("treefam-pdb")

# creating the treefam-alignments-and-trees and checking whether it already exists
if not os.path.isdir('treefam-pdb/treefam-alignments-and-trees'):
    os.mkdir("treefam-pdb/treefam-alignments-and-trees")

# creating the pdb-structure-files and checking whether it already exists
if not os.path.isdir('treefam-pdb/pdb-structure-files'):
    os.mkdir("treefam-pdb/pdb-structure-files")

# creating the contact-matrices and checking whether it already exists
if not os.path.isdir('treefam-pdb/contact-matrices'):
    os.mkdir("treefam-pdb/contact-matrices")

# creating the treefam-pdb-mappings and checking whether it already exists
if not os.path.isdir('treefam-pdb/treefam-pdb-mappings'):
    os.mkdir("treefam-pdb/treefam-pdb-mappings")

#creating summary.txt
open("treefam-pdb/summary.txt", "w+")
import requests
import json

# Function to fetch sequences from a URL
def fetch_sequences(url):
    response = requests.get(url)
    if response.status_code == 200:
        try:
            sequences = json.loads(response.text)
            if isinstance(sequences, list):
                return sequences
            else:
                raise ValueError("The fetched data is not a list")
        except json.JSONDecodeError:
            raise ValueError("Failed to decode JSON from the fetched data")
    else:
        raise Exception(f"Failed to fetch data from URL: {url}")

# Function to create a directory if it doesn't exist
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Function to process the sorted list and create directories
def process_sorted_list(sorted_list, base_dir):
    if not sorted_list:
        return

    current_directory = None
    first_digit = None

    for item in sorted_list:
        item_first_digit = str(item)[0]

        if item_first_digit != first_digit:
            first_digit = item_first_digit
            current_directory = os.path.join(base_dir, f"dir_{first_digit}")
            create_directory(current_directory)

        # Assuming you want to create files for each item
        file_path = os.path.join(current_directory, f"{item}.txt")
        with open(file_path, 'w') as file:
            file.write(str(item))

# Main script
if __name__ == "__main__":
    url = 'https://data.rcsb.org/rest/v1/holdings/current/entry_ids'  # Replace with the actual URL
    try:
        sequences = fetch_sequences(url)
        print(f"Fetched {len(sequences)} sequences.")

        # Directory base path
        base_dir = 'treefam-pdb/pdb-structure-files'
        create_directory(base_dir)  # Ensure the base directory exists

        # Process and sort sequences into directories
        process_sorted_list(sequences, base_dir)

        print(f"Sequences have been sorted into directories under {base_dir}")
    except Exception as e:
        print(str(e))
