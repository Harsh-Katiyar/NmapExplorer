import os
import platform
import re
import requests
import zipfile
import io
import subprocess


def get_default_nmap_scripts_dir():
    """Detects the operating system and returns the default Nmap scripts directory."""
    current_os = platform.system()
    if current_os in ["Linux", "Darwin"]:  # Darwin refers to macOS
        return "/usr/share/nmap/scripts/"
    elif current_os == "Windows":
        return "C:\\Program Files (x86)\\Nmap\\scripts\\"
    else:
        return None


def get_user_scripts_dir(default_dir):
    """Allows the user to specify a custom Nmap scripts directory or use the default."""
    print(f"Default Nmap scripts directory detected: {default_dir}")
    use_default = input("Do you want to use the default scripts directory? (y/n): ").strip().lower()
    if use_default == 'y':
        return default_dir
    else:
        custom_dir = input("Enter the full path to your Nmap scripts directory: ").strip()
        if os.path.exists(custom_dir):
            return custom_dir
        else:
            print(f"Custom directory not found: {custom_dir}")
            return None


def extract_script_metadata(script_path):
    """Extracts metadata (categories and description) from an NSE script."""
    metadata = {'categories': [], 'description': ''}
    try:
        with open(script_path, 'r', encoding='utf-8') as file:
            content = file.read()
            categories = re.findall(r'categories\s*=\s*{([^}]+)}', content)
            if categories:
                categories = [cat.strip().strip('"').strip("'") for cat in categories[0].split(',')]
                metadata['categories'] = categories
            description = re.search(r'description\s*=\s*"([^"]+)"', content)
            if description:
                metadata['description'] = description.group(1)
    except Exception as e:
        print(f"Error reading {script_path}: {e}")
    return metadata


def clone_repositories():
    """Clones the Nmap-vulners and vulscan repositories."""
    repos = [
        "https://github.com/vulnersCom/nmap-vulners.git",
        "https://github.com/scipag/vulscan.git"
    ]
    for repo in repos:
        try:
            print(f"Cloning {repo}...")
            subprocess.run(["git", "clone", repo], check=True)
        except Exception as e:
            print(f"Error cloning {repo}: {e}")


def download_additional_scripts():
    """Downloads additional NSE scripts from vulnscan and nmap-vulners repositories."""
    print("Cloning additional scripts from vulnscan and nmap-vulners...")
    clone_repositories()


def download_databases():
    """Downloads pre-installed vulnerability databases."""
    databases = {
        "scipvuldb.csv": "https://vuldb.com",
        "cve.csv": "https://cve.mitre.org",
        "securityfocus.csv": "https://www.securityfocus.com/bid/",
        "xforce.csv": "https://exchange.xforce.ibmcloud.com/",
        "exploitdb.csv": "https://www.exploit-db.com",
        "openvas.csv": "http://www.openvas.org",
        "securitytracker.csv": "https://www.securitytracker.com",  # End-of-life
        "osvdb.csv": "http://www.osvdb.org"  # End-of-life
    }

    print("Available databases to download:")
    for db in databases:
        print(f"{db} - {databases[db]}")

    choice = input("Do you want to download the databases? (y/n): ").strip().lower()
    if choice == 'y':
        for db, url in databases.items():
            response = requests.get(url)
            if response.ok:
                with open(db, 'wb') as f:
                    f.write(response.content)
                print(f"{db} downloaded successfully.")
            else:
                print(f"Failed to download {db}.")
    else:
        print("Database download skipped.")


def search_nmap_scripts(keyword, filter_type=None, filter_value=None):
    """Searches Nmap scripts based on a keyword and optional filters."""
    default_dir = get_default_nmap_scripts_dir()
    if not default_dir:
        print(f"Unsupported operating system: {platform.system()}")
        return

    nmap_scripts_dir = get_user_scripts_dir(default_dir)
    if not nmap_scripts_dir:
        return

    if not os.path.exists(nmap_scripts_dir):
        print(f"Nmap scripts directory not found: {nmap_scripts_dir}")
        return

    nse_files = [f for f in os.listdir(nmap_scripts_dir) if f.endswith('.nse')]

    # Add additional directories for cloned repos
    additional_dirs = ["nmap-vulners", "vulscan"]
    for additional_dir in additional_dirs:
        if os.path.exists(additional_dir):
            nse_files += [os.path.join(additional_dir, f) for f in os.listdir(additional_dir) if f.endswith('.nse')]

    matched_scripts = []

    for script in nse_files:
        script_path = os.path.join(nmap_scripts_dir, script)
        metadata = extract_script_metadata(script_path)

        is_match = False

        if keyword.lower() in script.lower() or (metadata['description'] and keyword.lower() in metadata['description'].lower()):
            is_match = True

        if is_match:
            if filter_type and filter_value:
                if filter_type == 'category':
                    if filter_value.lower() in [cat.lower() for cat in metadata['categories']]:
                        matched_scripts.append({'name': script, 'categories': metadata['categories'], 'description': metadata['description']})
                elif filter_type == 'description':
                    if filter_value.lower() in metadata['description'].lower():
                        matched_scripts.append({'name': script, 'categories': metadata['categories'], 'description': metadata['description']})
            else:
                matched_scripts.append({'name': script, 'categories': metadata['categories'], 'description': metadata['description']})

    unique_scripts = {script['name']: script for script in matched_scripts}.values()

    if unique_scripts:
        print(f"\nScripts matched with keyword '{keyword}':\n")
        for script in unique_scripts:
            print(f"Script Name   : {script['name']}")
            print(f"Categories    : {', '.join(script['categories']) if script['categories'] else 'N/A'}")
            print(f"Description   : {script['description'] if script['description'] else 'N/A'}\n")
    else:
        print(f"\nNo scripts found matching the keyword '{keyword}' with the specified filters.")


def main():
    print("=== Nmap NSE Script Search Utility ===\n")

    download_scripts = input("Do you want to download and use additional scripts from vulnscan and nmap-vulners? (y/n): ").strip().lower()
    if download_scripts == 'y':
        download_additional_scripts()

    download_databases()

    keyword = input("Enter a keyword to search for Nmap scripts: ").strip()
    if not keyword:
        print("Keyword cannot be empty.")
        return

    apply_filter = input("Do you want to apply additional filters? (y/n): ").strip().lower()
    filter_type = None
    filter_value = None

    if apply_filter == 'y':
        print("\nFilter Options:")
        print("1. Category")
        print("2. Description")
        filter_choice = input("Choose a filter type (1/2): ").strip()

        if filter_choice == '1':
            filter_type = 'category'
            filter_value = input("Enter the category to filter by (e.g., vuln, discovery): ").strip()
        elif filter_choice == '2':
            filter_type = 'description'
            filter_value = input("Enter a description keyword to filter by: ").strip()

    search_nmap_scripts(keyword, filter_type, filter_value)


if __name__ == '__main__':
    main()
