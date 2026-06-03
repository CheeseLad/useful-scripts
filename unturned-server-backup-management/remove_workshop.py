import os
import zipfile
import tempfile
import shutil

# Directory containing ZIP files
ZIP_DIRECTORY = r"F:\Backups\Cable Network\Cable Creative Roleplay Backups\2021-01"

# Folder inside ZIPs to remove
TARGET_FOLDER = "Servers/server/Workshop/"


def remove_folder_from_zip(zip_path, target_folder):
    print(f"Processing: {zip_path}")

    # Create temp ZIP
    fd, temp_zip_path = tempfile.mkstemp(suffix=".zip")
    os.close(fd)

    removed = False

    with zipfile.ZipFile(zip_path, 'r') as zin:
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zout:

            for item in zin.infolist():
                # Normalize slashes for ZIP paths
                item_path = item.filename.replace("\\", "/")

                # Skip files/folders inside target folder
                if item_path.startswith(target_folder):
                    removed = True
                    print(f"  Removed: {item_path}")
                    continue

                # Copy everything else
                data = zin.read(item.filename)
                zout.writestr(item, data)

    if removed:
        # Replace original ZIP
        shutil.move(temp_zip_path, zip_path)
        print("  ZIP updated.\n")
    else:
        os.remove(temp_zip_path)
        print("  Target folder not found.\n")


def main():
    for filename in os.listdir(ZIP_DIRECTORY):
        if filename.lower().endswith(".zip"):
            zip_path = os.path.join(ZIP_DIRECTORY, filename)
            remove_folder_from_zip(zip_path, TARGET_FOLDER)


if __name__ == "__main__":
    main()