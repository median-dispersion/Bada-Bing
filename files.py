import re
from pathlib import Path
import json

# =================================================================================================
# Only keep allowed characters in file names
# =================================================================================================
def sanitize_filename(filename: str) -> str:

    # Keep only allowed characters (A-Z, a-z, 0-9, "_", "-", " ")
    filename = re.sub(r"[^A-Za-z0-9_\-\. ]+", "_", filename)

    # Replace runs of 2+ whitespace characters with a single space
    filename = re.sub(r"\s{2,}", " ", filename)

    # Strip leading and trailing spaces
    filename = filename.strip()

    # Return the sanitized filename
    return filename

# =================================================================================================
# Save image data to disk
# =================================================================================================
def save_image_data(
    data: dict,
    directory: Path,
    save_metadata: bool = False
) -> dict:

    # Resolve the full directory path
    directory = directory.resolve()

    # Create image directory if it doesn't exists
    directory.mkdir(parents=True, exist_ok=True)

    # Generate the sanitized filename
    filename = sanitize_filename(f"{data['title']} - {data['copyright']} - {data['start_date']} - {data['end_date']}")

    # Construct the image filepath
    data["image_path"] = directory / f"{filename}.{data['file_format'].value}"

    # Save the image
    with open(data["image_path"], "wb") as file: file.write(data["image"])

    # Check if meta data should be saved
    if save_metadata:

        # Construct the metadata filepath
        data["metadata_path"] = directory / f"{filename}.json"

        # Create a copy of the data without the binary image data and paths converted to strings
        metadata = {
            key: str(value) if key in {"image_path", "metadata_path"} else value
            for key, value in data.items()
            if key != "image"
        }

        # Save the image metadata in an accompanying JSON file
        with open(data["metadata_path"], "w", encoding="utf-8") as file: json.dump(metadata, file, indent=4)

    # Return the image data
    return data