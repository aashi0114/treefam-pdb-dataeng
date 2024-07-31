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








import os
import requests
from pathlib import Path
import time

BASE_URL = "https://files.rcsb.org/download"
PDB_LIST_URL = "https://data.rcsb.org/rest/v1/holdings/current/entry_ids"
OUTPUT_DIR = "treefam-pdb/pdb-structure-files"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def fetch_pdb_ids():
    """Fetches the list of PDB IDs from the provided URL."""
    try:
        print(f"Fetching PDB IDs from {PDB_LIST_URL}")
        response = requests.get(PDB_LIST_URL)
        response.raise_for_status()
        pdb_ids = response.text.strip().split(',')
        # Remove any extraneous characters like quotes or brackets
        pdb_ids = [pdb_id.strip('"[]') for pdb_id in pdb_ids]
        return pdb_ids
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch PDB IDs: {e}")
        return []

def download_file(pdb_id, outdir):
    """Downloads a single PDB file and saves it to the specified directory."""
    url = f"{BASE_URL}/{pdb_id}.pdb.gz"
    outpath = os.path.join(outdir, f"{pdb_id}.pdb.gz")
    attempt = 0

    while attempt < MAX_RETRIES:
        try:
            print(f"Attempting to download {url} to {outpath} (Attempt {attempt + 1})")
            response = requests.get(url)
            if response.status_code == 200:
                with open(outpath, 'wb') as f:
                    f.write(response.content)
                print(f"Successfully downloaded {url}")
                return
            else:
                print(f"Received status code {response.status_code} for {url}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {e}")

        attempt += 1
        time.sleep(RETRY_DELAY)

    print(f"Failed to download {url} after {MAX_RETRIES} attempts")

def sort_files(indir, outdir):
    """Sorts downloaded files into directories based on the first character of the PDB ID."""
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        x=0

    print(f"Sorting files from {indir} into {outdir}")
    for filepath in Path(indir).glob("*.pdb.gz"):
        filename = filepath.name
        pdb_id = filename[:4]
        subdir = os.path.join(outdir, f"dir_{pdb_id[0]}")
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        new_path = os.path.join(subdir, filename)
        os.rename(filepath, new_path)
        print(f"Moved {filename} to {new_path}")

def main():
    # Fetch PDB IDs from the RCSB PDB
    pdb_ids = fetch_pdb_ids()
    if not pdb_ids:
        print("No PDB IDs retrieved. Exiting.")
        return

    # Create output directories
    tempdir = Path("temp")
    tempdir.mkdir(parents=True, exist_ok=True)
    outdir = Path(OUTPUT_DIR)
    outdir.mkdir(parents=True, exist_ok=True)

    # Download each PDB file
    for pdb_id in pdb_ids:
        download_file(pdb_id, tempdir)

    # Sort downloaded files
    sort_files(tempdir, outdir)
    print(f"Download and sorting complete. Files are located in {OUTPUT_DIR}")

    # Clean up temporary directory
    for file in tempdir.glob("*"):
        file.unlink()
    tempdir.rmdir()

if __name__ == "__main__":
    main()
