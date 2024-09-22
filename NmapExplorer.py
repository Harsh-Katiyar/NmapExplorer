import os
import re
import platform
import requests
import zipfile
import io
from tabulate import tabulate

# Color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# Function to detect OS
def detect_os():
    current_os = platform.system().lower()
    print(f"Running on {current_os.capitalize()}")
    return current_os

# Function to search for a specific file by name in the directory and subdirectories
def search_file_in_directory(directory, file_name):
    file_name = file_name.lower()
    found_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file_name in file.lower():
                found_files.append(os.path.join(root, file))
    return found_files

# Function to download and extract the zip file
def download_and_extract_zip(url, extract_to='.'):
    try:
        print(f"{Colors.OKBLUE}Downloading zip file from {url}...{Colors.ENDC}")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            print(f"{Colors.OKGREEN}Download successful. Extracting...{Colors.ENDC}")
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(extract_to)
            abs_extract_path = os.path.abspath(extract_to)
            print(f"{Colors.OKGREEN}Extraction complete. Files extracted to: {abs_extract_path}{Colors.ENDC}")
            return abs_extract_path
        else:
            print(f"{Colors.FAIL}Failed to download zip file. Status code: {response.status_code}{Colors.ENDC}")
            return None
    except Exception as e:
        print(f"{Colors.FAIL}An error occurred during download or extraction: {e}{Colors.ENDC}")
        return None

# Function to prompt the user to download and configure
def prompt_for_download():
    choice = input("Would you like to download and configure the tool? (y/n): ").lower()
    if choice == 'y':
        download_url = "https://github.com/Harsh-Katiyar/NmapExplorer/blob/main/nmap.zip?raw=true"
        extract_path = download_and_extract_zip(download_url, extract_to='nmap_tool')
        if extract_path:
            print(f"\nExtracted files are located at: {extract_path}")
            print("Please follow the README for configuration steps, if any.")
            return extract_path
    else:
        print("Skipping download and configuration.")
        return None

# Main function
def main():
    current_os = detect_os()
    default_search_path = None

    # Set default search path for Linux
    if current_os == 'linux':
        default_search_path = os.path.expanduser('/usr/share/nmap')  # Update with your Nmap scripts path
        print(f"Default search path set to: {default_search_path}")

    # Prompt for download and configure
    extract_path = prompt_for_download()

    # Decide search path
    if not extract_path:
        if default_search_path:
            use_default = input(f"Would you like to search in the default Nmap script folder ({default_search_path})? (y/n): ").lower()
            if use_default == 'y':
                file_path = default_search_path
            else:
                while True:
                    file_path = input("Enter the full path of the directory to search in: ").strip()
                    if os.path.isdir(file_path):
                        break
                    else:
                        print(f"{Colors.FAIL}Invalid directory. Please try again.{Colors.ENDC}")
        else:
            file_path = input("Enter the full path of the directory to search in: ").strip()

        file_name = input("Enter the file name to search for: ").strip()
        print(f"\nSearching for file '{file_name}' in '{file_path}'...\n")
        results = search_file_in_directory(file_path, file_name)

    else:
        file_name = input("Enter the file name to search: ").strip()
        print(f"\nSearching for file '{file_name}' in the extracted folder...\n")
        results = search_file_in_directory(extract_path, file_name)

    display_choice = input("How would you like to display the results? (1: Full Paths, 2: File Names Only): ").strip()
    show_full_path = display_choice == '1'

    display_results(results, show_full_path)

# Function to display results in a tabular format based on user choice
def display_results(results, show_full_path):
    if results:
        if show_full_path:
            headers = ["Index", "File Path"]
            table_data = [(i + 1, result) for i, result in enumerate(results)]
        else:
            headers = ["Index", "File Name"]
            table_data = [(i + 1, os.path.basename(result)) for i, result in enumerate(results)]

        print("\nSearch Results:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    else:
        print("No matches found.")

if __name__ == "__main__":
    main()
