import os
import re
import platform
import requests
import zipfile
import io
from tabulate import tabulate  # Ensure to install this via pip

# Function to detect OS
def detect_os():
    current_os = platform.system().lower()
    if "windows" in current_os:
        print("Running on Windows")
    elif "linux" in current_os:
        print("Running on Linux")
    elif "darwin" in current_os:  # Darwin is macOS
        print("Running on macOS")
    else:
        print(f"Unsupported OS: {current_os}")
    return current_os

# Function to search for a specific file by name in the extracted directory and subdirectories
def search_file_in_directory(directory, file_name):
    file_name = file_name.lower()  # Make the search case-insensitive
    found_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file_name in file.lower():
                found_files.append(os.path.join(root, file))  # Full path
    return found_files

# Function to download and extract the zip file
def download_and_extract_zip(url, extract_to='.'):
    try:
        print(f"Downloading zip file from {url}...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            print("Download successful. Extracting...")
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(extract_to)
            abs_extract_path = os.path.abspath(extract_to)
            print(f"Extraction complete. Files extracted to: {abs_extract_path}")
            return abs_extract_path  # Return the absolute path to the extracted directory
        else:
            print(f"Failed to download zip file. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred during download or extraction: {e}")
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

# Main function
def main():
    # Detect OS
    current_os = detect_os()

    # Prompt for download and configure
    extract_path = prompt_for_download()

    # If the user chose not to download, ask for the file name and path
    if not extract_path:
        file_path = input("Enter the full path of the directory to search in: ").strip()
        file_name = input("Enter the file name to search for: ").strip()

        # Search for the file in the specified directory and its subdirectories
        print(f"\nSearching for file '{file_name}' in '{file_path}'...\n")
        results = search_file_in_directory(file_path, file_name)

    else:
        # User input for the file name to search in the extracted directory
        file_name = input("Enter the file name to search: ").strip()

        # Search for the file in the extracted directory and subdirectories
        print(f"\nSearching for file '{file_name}' in the extracted folder...\n")
        results = search_file_in_directory(extract_path, file_name)

    # Ask user how they want to display results
    display_choice = input("How would you like to display the results? (1: Full Paths, 2: File Names Only): ").strip()
    show_full_path = display_choice == '1'

    # Display results based on user's choice
    display_results(results, show_full_path)

if __name__ == "__main__":
    main()
