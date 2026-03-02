from enumerators import Region, Resolution, FileFormat
import requests
import time
from datetime import datetime
from hashlib import sha256
import logger

# =================================================================================================
# Get metadata
# =================================================================================================
def get_metadata(
    region: Region = Region.EN_US,
    day_index: int = 0,
    number_of_images: int = 1,
    timeout_seconds: int = 10,
    attempts: int = 10,
    attempt_delay_seconds: int = 1
) -> list:

    # Metadata URL
    url = "https://www.bing.com/HPImageArchive.aspx"

    # Request parameters
    parameters = {
        "format": "js", # JSON
        "mkt": region,
        "idx": day_index,
        "n": number_of_images
    }

    # Loop until a request succeeds or the maximum number of attempts is reached
    for attempt in range(0, attempts):

        try:

            logger.info(f"Attempt {attempt} trying to get metadata from '{url}?format={parameters['format']}&mkt={parameters['mkt']}&idx={parameters['idx']}&n={parameters['n']}'")

            # Request metadata
            response = requests.get(url=url, params=parameters, timeout=timeout_seconds)
            response.raise_for_status()
            response_data = response.json()

            # List of metadata
            metadata = []

            # Extract metadata from response
            for data_entry in response_data["images"]:

                # Add the extracted metadata
                metadata.append({
                    "url": f"https://www.bing.com{data_entry['urlbase']}",
                    "title": data_entry["title"],
                    "copyright": data_entry["copyright"],
                    "copyright_url": data_entry["copyrightlink"],
                    "region": region,
                    "start_date": data_entry["startdate"],
                    "full_start_date": data_entry["fullstartdate"],
                    "end_date": data_entry["enddate"]
                })

            logger.success("Successfully gotten metadata")

            # Return the extracted metadata
            return metadata

        # If an exception occurs do nothing
        except Exception as exception:

            logger.error(f"Failed to get metadata, exception: {exception}")

        logger.info(f"Next attempt to get metadata in {attempt_delay_seconds} second(s)")

        # Delay the next attempt
        time.sleep(attempt_delay_seconds)

    logger.error(f"Could not get metadata in {attempts} attempt(s)")

    # Raise an exception if the maximum number of attempts have been reached
    raise Exception("Maximum number of request attempts reached!")

# =================================================================================================
# Get image data
# =================================================================================================
def get_image_data(
    data: dict,
    resolution: Resolution = Resolution.PIXEL_3840_2160,
    file_format: FileFormat = FileFormat.JPG,
    timeout_seconds: int = 10,
    attempts: int = 10,
    attempt_delay_seconds: int = 1
) -> dict:

    # Image URL
    url = f"{data['url']}_{resolution.value}.{file_format.value}"

    # Add to image data
    data["url"] = url
    data["resolution"] = resolution
    data["file_format"] = file_format

    # Loop until a request succeeds or the maximum number of attempts is reached
    for attempt in range(0, attempts):

        try:

            logger.info(f"Attempt {attempt} trying to get image data from '{url}'")

            # Request image
            response = requests.get(url=url, timeout=timeout_seconds)
            response.raise_for_status()

            # Add the image to the image data
            data["image"] = response.content

            # Add the download date to the image data
            data["download_date"] = datetime.now().astimezone().isoformat()

            # Add image data SHA-256 checksum
            data["checksum_sha256"] = sha256(data["image"]).hexdigest()

            logger.success("Successfully gotten image data")

            # Return the image data
            return data

        # If an exception occurs do nothing
        except Exception as exception:

            logger.error(f"Failed to get image data, exception: {exception}")

        logger.info(f"Next attempt to get image data in {attempt_delay_seconds} second(s)")

        # Delay the next attempt
        time.sleep(attempt_delay_seconds)

    logger.error(f"Could not get image data in {attempts} attempt(s)")

    # Raise an exception if the maximum number of attempts have been reached
    raise Exception("Maximum number of request attempts reached!")