import os
import re
import zipfile

# Input combined YAML file
INPUT_FILE = "YAML SImulator 2/mentalyc_all_specs.yaml"

# Base output folder for the split files
BASE_DIR = "mentalyc_sim_package_v3"


def split_yaml_by_file_comment(input_path: str, base_dir: str):
    os.makedirs(base_dir, exist_ok=True)

    current_path = None
    current_file = None

    file_pattern = re.compile(r'\s*#\s*file:\s*(.+)$')

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            m = file_pattern.match(line)
            if m:
                # Close previous file if open
                if current_file is not None:
                    current_file.close()
                    current_file = None

                rel_path = m.group(1).strip()
                current_path = os.path.join(base_dir, rel_path)

                # Make sure the directory exists
                os.makedirs(os.path.dirname(current_path), exist_ok=True)

                # Open new file for writing
                current_file = open(current_path, "w", encoding="utf-8")
                # Do NOT write the "# file:" line itself
                continue

            if current_file is not None:
                current_file.write(line)

    if current_file is not None:
        current_file.close()


def zip_folder(folder: str, zip_name: str):
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(folder):
            for fname in files:
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, folder)
                # Put everything under the top-level folder name inside the zip
                arcname = os.path.join(os.path.basename(folder), rel_path)
                z.write(full_path, arcname=arcname)


if __name__ == "__main__":
    print(f"Splitting {INPUT_FILE} into structured files under {BASE_DIR}...")
    split_yaml_by_file_comment(INPUT_FILE, BASE_DIR)
    print("Split complete.")

    zip_name = BASE_DIR + ".zip"
    print(f"Creating zip: {zip_name} ...")
    zip_folder(BASE_DIR, zip_name)
    print("Done.")
