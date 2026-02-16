import argparse
from enumerators import Region, Resolution, FileFormat
from pathlib import Path

# =================================================================================================
# Positive integer launch argument type
# =================================================================================================
def positive_integer(value: str) -> int:

    # Parse the value as an integer
    value = int(value)

    # If the integer is not positive
    if value < 1:

        # Raise an exception
        raise argparse.ArgumentTypeError(f"{value} is invalid; value must be greater than or equal to 1!")

    # Return the positive integer
    return value

# =================================================================================================
# Get launch arguments
# =================================================================================================
def get_arguments():

    # Initialize the argument parser
    parser = argparse.ArgumentParser(
        prog = "Bada Bing!",
        description = "A simple CLI tool that automatically downloads Bing's daily wallpaper."
    )

    # Add launch arguments

    parser.add_argument(
        "--region",
        type = Region,
        choices = [region.value for region in Region],
        default = Region.EN_US,
        help = "Sets the server region from where the images are downloaded. The default value is en-US."
    )

    parser.add_argument(
        "--day_index",
        type = int,
        choices = range(0, 8),
        default = 0,
        help = "Specifies the starting day in the past from which images are downloaded. 0 represents today, 1 represents yesterday, 2 represents two days ago, and so on. The default value is 0."
    )

    parser.add_argument(
        "--number_of_images",
        type = int,
        choices = range(1, 9),
        default = 1,
        help = "Controls how many images are downloaded. For example, 1 only downloads today's image, 2 downloads today's and yesterday's image, and so on. If --day_index is set to something different than 0, it will be N images downloaded starting from that day's index into the past. The default value is 1."
    )

    parser.add_argument(
        "--resolution",
        type = Resolution,
        choices = [resolution.value for resolution in Resolution],
        default = Resolution.PIXEL_3840_2160,
        help = "Sets the native resolution of the image. The default value is UHD (3840 x 2160 px)."
    )

    parser.add_argument(
        "--file_format",
        type = FileFormat,
        choices = [file_format.value for file_format in FileFormat],
        default = FileFormat.JPG,
        help = "Sets the image format of the downloaded image. The default value is jpg."
    )

    parser.add_argument(
        "--request_timeout_seconds",
        type = positive_integer,
        default = 10,
        help = "Sets the number of seconds before a request times out. The default value is 10 seconds."
    )

    parser.add_argument(
        "--request_attempts",
        type = positive_integer,
        default = 10,
        help = "Sets the number of attempts before a request fails. The default value is 10."
    )

    parser.add_argument(
        "--request_attempt_delay_seconds",
        type = positive_integer,
        default = 1,
        help = "Set the number of seconds in between request attempts. The default is 1 second."
    )

    parser.add_argument(
        "--image_directory",
        type = Path,
        default = "./Images",
        help = "Specifies the directory path where the images are downloaded to. The default value is './Images'."
    )

    parser.add_argument(
        "--save_metadata",
        type = bool,
        choices = [True, False],
        default = True,
        help = "Controls if the image metadata should be saved in an accompanying JSON file. The default value is True."
    )

    # Return the parsed arguments
    return parser.parse_args()