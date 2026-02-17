from arguments import get_arguments
from database import initialize_database
from daemon import run_daemon
from bing import get_metadata, get_image_data
from files import save_image_data

# Main
if __name__ == "__main__":

    # Get launch arguments
    arguments = get_arguments()

    # Check if running in daemon mode
    if arguments.daemon:

        # Initialize the database
        initialize_database()

        # Run the daemon
        run_daemon(arguments)

    # If not running in daemon mode
    else:

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
        for metadata_entry in metadata:

            # Add image data to the list of image data
            image_data.append(get_image_data(
                metadata_entry,
                arguments.resolution,
                arguments.file_format,
                arguments.request_timeout_seconds,
                arguments.request_attempts,
                arguments.request_attempt_delay_seconds
            ))

        # For every entry in the list of image data
        for image_data_entry in image_data:

            # Save the image data to disk
            save_image_data(
                image_data_entry,
                arguments.image_directory,
                arguments.save_metadata
            )