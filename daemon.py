from argparse import Namespace
from database import get_session
from datetime import datetime
import time
from bing import get_metadata, get_image_data
from files import save_image_data, delete_image_data
from pathlib import Path

# =================================================================================================
# Run the daemon loop
# =================================================================================================
def run_daemon(
    arguments: Namespace,
    start_date_value: str
) -> None:

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
                    arguments.download_directory,
                    arguments.save_metadata
                )

                # Update values
                start_date_value = data["start_date"]
                update_date = datetime.now().astimezone().isoformat()

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
                            update_date
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

                    # Get the total number of downloaded images
                    downloaded_images = session.execute("""
                        SELECT COUNT(image_path) AS downloaded_images
                        FROM images;
                    """).fetchone()["downloaded_images"]

                # Check if only a specific number of images should be kept
                # And if the number of downloaded images exceeds that number
                if arguments.keep_images > -1 and arguments.keep_images < downloaded_images:

                    # Calculate the number of images that need to be deleted
                    images_to_delete = downloaded_images - arguments.keep_images

                    # Get a database session
                    with get_session() as session:

                        # Select the number of images that need to be deleted ordered by download date
                        data_to_delete = session.execute(
                            """
                                SELECT id, checksum_sha256, image_path, metadata_path
                                FROM images
                                WHERE image_path IS NOT NULL
                                ORDER BY download_date ASC
                                LIMIT ?;
                            """,
                            (images_to_delete,)
                        ).fetchall()

                        # Get the ids of rows that need to be updated
                        ids_to_update = [(entry["id"],) for entry in data_to_delete]

                        # Set the image_path and metadata_path to NULL for all images that should be deleted
                        session.executemany(
                            """
                                UPDATE images
                                SET image_path = NULL, metadata_path = NULL
                                WHERE id = ?;
                            """,
                            ids_to_update
                        )

                    # For ever image in the data that should be deleted
                    for image_data_to_delete in data_to_delete:

                        # Extract the values
                        image_path = Path(image_data_to_delete["image_path"])
                        checksum_sha256 = image_data_to_delete["checksum_sha256"]
                        metadata_path = Path(image_data_to_delete["metadata_path"]) if image_data_to_delete["metadata_path"] is not None else None

                        # Delete the image data from disk
                        delete_image_data(
                            image_path,
                            checksum_sha256,
                            metadata_path
                        )

            # Sleep until the next update
            time.sleep(arguments.update_hours * 3600)

        # If an exception occurs
        except Exception:

            # Retry after the failure timeout
            time.sleep(arguments.update_failure_timeout_hours * 3600)

# =================================================================================================
# Start the daemon
# =================================================================================================
def start_daemon(arguments: Namespace) -> None:

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

    # Run the main daemon loop
    run_daemon(arguments, start_date_value)