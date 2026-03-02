from arguments import get_arguments
import logger
from database import initialize_database
from daemon import run_daemon
from bing import get_metadata, get_image_data
from files import save_image_data

# Main
if __name__ == "__main__":

    # Get launch arguments
    arguments = get_arguments()

    # Setup logger
    logger.verbose = arguments.verbose
    logger.file = arguments.log_file
    logger.disable_escape_codes = arguments.disable_escape_codes

    # Check if running in daemon mode
    if arguments.daemon:

        logger.info("Running in daemon mode")

        # Initialize the database
        initialize_database()

        # Run the daemon
        run_daemon(arguments)

    # If not running in daemon mode
    else:

        logger.info("Running in manual mode")

        # Get the metadata
        data = get_metadata(
            arguments.region,
            arguments.day_index,
            arguments.images,
            arguments.request_timeout_seconds,
            arguments.request_attempts,
            arguments.request_attempt_delay_seconds
        )

        # For every entry in the data list
        for data_entry in data:

            # Add image data to the entry
            get_image_data(
                data_entry,
                arguments.resolution,
                arguments.file_format,
                arguments.request_timeout_seconds,
                arguments.request_attempts,
                arguments.request_attempt_delay_seconds
            )

        # For every entry in the data list
        for data_entry in data:

            # Save the image data to disk
            save_image_data(
                data_entry,
                arguments.download_directory,
                arguments.save_metadata
            )