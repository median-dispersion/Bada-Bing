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
    save_metadata: bool = True
) -> None:

    # Generate the sanitized filename
    filename = sanitize_filename(f"{data['title']} - {data['copyright']} - Form {data['start_date']} to {data['end_date']}")

    # Construct the image filepath
    path = directory / f"{filename}.{data['file_format'].value}"

    # Create image directory if it doesn't exists
    directory.mkdir(parents=True, exist_ok=True)

    # Save the image
    with open(path, "wb") as file: file.write(data["image"])

    # Check if meta data should be saved
    if save_metadata:

        # Remove the binary image data
        data.pop("image")

        # Construct the metadata filepath
        path = directory / f"{filename}.json"

        # Save the image metadata in an accompanying JSON file
        with open(path, "w", encoding="utf-8") as file: json.dump(data, file, indent=4)