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
            SELECT start_date_value, update_date
            FROM status
            WHERE id = (SELECT MAX(id) FROM status);
        """).fetchone()

    # Extract the start date value from the status
    start_date_value = status["start_date_value"]

    # Extract the update date from the status
    update_date = datetime.fromisoformat(status["update_date"])

    # Calculate how long ago the last update was in seconds
    seconds_since_update = (datetime.now().astimezone() - update_date).total_seconds()

    # Get the update interval in seconds
    update_interval_seconds = arguments.update_hours * 3600

    # Check if the update interval since the last update has not been reached
    if seconds_since_update < update_interval_seconds:

        # Delay the next update by the remaining time until the update interval has been reached
        time.sleep(update_interval_seconds - seconds_since_update)

    # Loop forever
    while True:

        try:

            # Get the image metadata
            data = get_metadata(
                arguments.region,
                0,
                1,
                arguments.request_timeout_seconds,
                arguments.request_attempts,
                arguments.request_attempt_delay_seconds
            )[0]

            # Check if there is a new image available
            if int(start_date_value) < int(data["start_date"]):

                # Get the image data
                get_image_data(
                    data,
                    arguments.resolution,
                    arguments.file_format,
                    arguments.request_timeout_seconds,
                    arguments.request_attempts,
                    arguments.request_attempt_delay_seconds
                )

                # Save the image data to disk and get the file paths
                save_image_data(
                    data,
                    arguments.image_directory,
                    arguments.save_metadata
                )

                # Update values
                start_date_value = data["start_date"]
                update_date = datetime.now().astimezone()

                # Get a database session
                with get_session() as session:

                    # Update the status table with the latest update status
                    session.execute(
                        """
                            UPDATE status
                            SET start_date_value = ?, update_date = ?
                            WHERE id = (SELECT MAX(id) FROM status);
                        """,
                        (
                            start_date_value,
                            update_date.isoformat()
                        )
                    )

                    # Insert image data into database
                    session.execute(
                        """
                            INSERT INTO images (
                                url,
                                title,
                                copyright,
                                copyright_url,
                                region,
                                start_date,
                                full_start_date,
                                end_date,
                                resolution,
                                file_format,
                                download_date,
                                checksum_sha256,
                                image_path,
                                metadata_path
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            data["url"],
                            data["title"],
                            data["copyright"],
                            data["copyright_url"],
                            data["region"],
                            data["start_date"],
                            data["full_start_date"],
                            data["end_date"],
                            data["resolution"],
                            data["file_format"],
                            data["download_date"],
                            data["checksum_sha256"],
                            str(data["image_path"]),
                            str(data["metadata_path"]) if data.get("metadata_path") is not None else None
                        )
                    )

            # Sleep until the next update
            time.sleep(arguments.update_hours * 3600)

        # If an exception occurs
        except Exception:

            # Retry after the failure timeout
            time.sleep(arguments.update_failure_timeout_hours * 3600)