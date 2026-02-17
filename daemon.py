from argparse import Namespace
from database import get_session
from datetime import datetime
import time
from bing import get_metadata, get_image_data
from files import save_image_data

# =================================================================================================
# Run the daemon loop
# =================================================================================================
def run_daemon(arguments: Namespace) -> None:

    # Get a database session
    with get_session() as session:

        # Select the latest status from the database
        status = session.execute("""
            SELECT last_start_date_value, last_update_date
            FROM status
            WHERE id = (SELECT MAX(id) FROM status);
        """).fetchone()

    # Extract the last start date value from the status
    last_start_date_value = status["last_start_date_value"]

    # Extract the last update date from the status
    last_update_date = datetime.fromisoformat(status["last_update_date"])

    # Calculate how long ago the last update was in seconds
    seconds_since_update = (datetime.now().astimezone() - last_update_date).total_seconds()

    # Get the update interval in seconds
    update_interval_seconds = arguments.update_hours * 3600

    # Check if the update interval since the last update has not been reached
    if seconds_since_update < update_interval_seconds:

        # Delay the next update by the remaining time until the update interval has been reached
        time.sleep(update_interval_seconds - seconds_since_update)

    # Loop forever
    while True:

        try:

            # Get the metadata
            metadata = get_metadata(
                arguments.region,
                0,
                1,
                arguments.request_timeout_seconds,
                arguments.request_attempts,
                arguments.request_attempt_delay_seconds
            )[0]

            # Check if there is a new image available
            if int(last_start_date_value) < int(metadata["start_date"]):

                # Get the image data
                image_data = get_image_data(
                    metadata,
                    arguments.resolution,
                    arguments.file_format,
                    arguments.request_timeout_seconds,
                    arguments.request_attempts,
                    arguments.request_attempt_delay_seconds
                )

                # Save the image data to disk
                save_image_data(
                    image_data,
                    arguments.image_directory,
                    arguments.save_metadata
                )

                # Update values
                last_start_date_value = metadata["start_date"]
                last_update_date = datetime.now().astimezone()

                # Get a database session
                with get_session() as session:

                    # Update the status table with the latest update status
                    session.execute(
                        """
                            UPDATE status
                            SET last_start_date_value = ?, last_update_date = ?
                            WHERE id = (SELECT MAX(id) FROM status);
                        """,
                        (
                            last_start_date_value,
                            last_update_date.isoformat()
                        )
                    )

            # Sleep until the next update
            time.sleep(arguments.update_hours * 3600)

        # If an exception occurs
        except Exception:

            # Retry after the failure timeout
            time.sleep(arguments.update_failure_timeout_hours * 3600)