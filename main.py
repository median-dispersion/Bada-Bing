from arguments import get_arguments
from bing import get_metadata, get_image_data
from storage import save_image_data

# Main
if __name__ == "__main__":

    # Get launch arguments
    arguments = get_arguments()

    # Get metadata
    metadata = get_metadata(
        arguments.region,
        arguments.day_index,
        arguments.number_of_images,
        arguments.request_timeout_seconds,
        arguments.request_attempts,
        arguments.request_attempt_delay_seconds
    )

    # List of image data
    image_data = []

    # For every entry in the list of metadata
    for entry in metadata:

        # Add image data to the list of image data
        image_data.append(get_image_data(
            entry,
            arguments.resolution,
            arguments.file_format,
            arguments.request_timeout_seconds,
            arguments.request_attempts,
            arguments.request_attempt_delay_seconds
        ))

    # For every entry in the list of image data
    for entry in image_data:

        # Save the image data to disk
        save_image_data(
            entry,
            arguments.image_directory,
            arguments.save_metadata
        )