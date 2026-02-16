from enumerators import Region, Resolution, FileFormat
import requests
import time

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

            # Request metadata
            response = requests.get(url=url, params=parameters, timeout=timeout_seconds)
            response.raise_for_status()
            data = response.json()

            # List of metadata
            metadata = []

            # Extract metadata from response
            for entry in data["images"]:

                # Add the extracted metadata
                metadata.append({
                    "url": f"https://www.bing.com{entry['urlbase']}",
                    "title": entry["title"],
                    "copyright": entry["copyright"],
                    "copyright_url": entry["copyrightlink"],
                    "region": region,
                    "start_date": entry["startdate"],
                    "full_start_date": entry["fullstartdate"],
                    "end_date": entry["enddate"]
                })

            # Return the extracted metadata
            return metadata

        # If an exception occurs do nothing
        except Exception: pass

        # Delay the next attempt
        time.sleep(attempt_delay_seconds)

    # Raise an exception if the maximum number of attempts have been reached
    raise Exception("Maximum number of request attempts reached!")

# =================================================================================================
# Get image data
# =================================================================================================
def get_image_data(
    metadata: dict,
    resolution: Resolution = Resolution.PIXEL_3840_2160,
    file_format: FileFormat = FileFormat.JPG,
    timeout_seconds: int = 10,
    attempts: int = 10,
    attempt_delay_seconds: int = 1
) -> dict:

    # Image URL
    url = f"{metadata['url']}_{resolution.value}.{file_format.value}"

    # Image data
    data = metadata
    data["url"] = url
    data["resolution"] = resolution
    data["file_format"] = file_format

    # Loop until a request succeeds or the maximum number of attempts is reached
    for attempt in range(0, attempts):

        try:

            # Request image
            response = requests.get(url=url, timeout=timeout_seconds)
            response.raise_for_status()

            # Add the image to the image data
            data["image"] = response.content

            # Return the image data
            return data

        # If an exception occurs do nothing
        except Exception: pass

        # Delay the next attempt
        time.sleep(attempt_delay_seconds)

    # Raise an exception if the maximum number of attempts have been reached
    raise Exception("Maximum number of request attempts reached!")