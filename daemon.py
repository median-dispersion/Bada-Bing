from argparse import Namespace
from database import get_session
from datetime import datetime
import time
from bing import get_metadata, get_image_data
from files import save_image_data, delete_image_data
from pathlib import Path
import logger

# =================================================================================================
# Get the latest status from the database
# =================================================================================================
def get_status() -> dict:

    # Get a database session
    with get_session() as session:

        # Select the latest status from the database
        status = session.execute("""
            SELECT start_date_value, update_date
            FROM status
            WHERE id = (SELECT MAX(id) FROM status);
        """).fetchone()

    # Extract the start date value from the status
    start_date_value = str(status["start_date_value"])

    # Extract the update date from the status
    update_date = datetime.fromisoformat(status["update_date"])

    logger.info(f"Last image start date was '{start_date_value}', updated on {update_date.isoformat()}")

    # Return the latest status
    return {
        "start_date_value": start_date_value,
        "update_date": update_date
    }

# =================================================================================================
# Delay the next update
# =================================================================================================
def delay_update(
    update_date: datetime,
    update_hours: int
) -> None:

    # Calculate how long ago the last update was in seconds
    seconds_since_update = (datetime.now().astimezone() - update_date).total_seconds()

    # Get the update interval in seconds
    update_interval_seconds = update_hours * 3600

    # Check if the update interval since the last update has not been reached
    if seconds_since_update < update_interval_seconds:

        logger.info(f"Delaying the next update by {round(((update_interval_seconds - seconds_since_update) / 3600) * 10) / 10} hour(s)")

        # Delay the next update by the remaining time until the update interval has been reached
        time.sleep(update_interval_seconds - seconds_since_update)

# =================================================================================================
# Store image data in database
# =================================================================================================
def store_image_data(data: dict) -> int:

    logger.info("Storing new image data in the database")

    # Get a database session
    with get_session() as session:

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
                str(data["image_path"]) if data.get("image_path") is not None else None,
                str(data["metadata_path"]) if data.get("metadata_path") is not None else None
            )
        )

        # Get the total number of saved images
        saved_images = session.execute("""
            SELECT COUNT(image_path) AS saved_images
            FROM images;
        """).fetchone()["saved_images"]

    logger.success("Successfully stored image data in the database")

    # Return the number of images that are saved on disk
    return int(saved_images)

# =================================================================================================
# Delete old image files
# =================================================================================================
def prune_images_files(
    keep_images: int,
    saved_images: int
) -> None:

    # Check if all images should be kept
    # Or if the number of saved images is less than the number of images to keep
    # If so do nothing
    if keep_images <= -1 or keep_images >= saved_images: return

    # Calculate the number of images that need to be deleted
    images_to_delete = saved_images - keep_images

    logger.info(f"{images_to_delete} old image(s) will be deleted from disk")

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
        checksum_sha256 = str(image_data_to_delete["checksum_sha256"])
        metadata_path = Path(image_data_to_delete["metadata_path"]) if image_data_to_delete["metadata_path"] is not None else None

        # Delete the image data from disk
        delete_image_data(
            image_path,
            checksum_sha256,
            metadata_path
        )

    logger.success("Successfully deleted old image(s)")

# =================================================================================================
# Update the status
# =================================================================================================
def update_status(start_date_value: str) -> None:

    # Get a database session
    with get_session() as session:

        # Update the status
        session.execute(
            """
                UPDATE status
                SET start_date_value = ?, update_date = ?
                WHERE id = (SELECT MAX(id) FROM status);
            """,
            (
                start_date_value,
                datetime.now().astimezone().isoformat()
            )
        )

# =================================================================================================
# Run the daemon
# =================================================================================================
def run_daemon(arguments: Namespace) -> None:

    # Get the latest status
    status = get_status()

    # Try to delay the next update
    delay_update(
        status["update_date"],
        arguments.update_hours
    )

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
            if int(status['start_date_value']) < int(data["start_date"]):

                # Update start date value
                status["start_date_value"] = data["start_date"]

                logger.success(f"A new image with the start date '{status['start_date_value']}' is available")

                # Get the image data
                get_image_data(
                    data,
                    arguments.resolution,
                    arguments.file_format,
                    arguments.request_timeout_seconds,
                    arguments.request_attempts,
                    arguments.request_attempt_delay_seconds
                )

                # Check if at least 1 image should be kept
                if arguments.keep_images != 0:

                    # Save the image data to disk and get the file paths
                    save_image_data(
                        data,
                        arguments.download_directory,
                        arguments.save_metadata
                    )

                # Store image data in database
                # Get the new number of images saved on disk
                saved_images = store_image_data(data)

                # Delete old images that should not be kept
                prune_images_files(
                    arguments.keep_images,
                    saved_images
                )

            # Update the status
            update_status(status["start_date_value"])

            logger.info(f"Going to sleep for {arguments.update_hours} hour(s)")

            # Sleep until the next update
            time.sleep(arguments.update_hours * 3600)

        # If an exception occurs
        except Exception as exception:

            logger.error(f"Update failed, exception: {exception}")
            logger.info(f"Retrying in {arguments.update_failure_timeout_hours} hour(s)")

            # Retry after the failure timeout
            time.sleep(arguments.update_failure_timeout_hours * 3600)