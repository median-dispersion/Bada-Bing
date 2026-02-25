import argparse
from enumerators import Region, Resolution, FileFormat
from pathlib import Path

# =================================================================================================
# Constrained integer argument type
# =================================================================================================
def constrained_integer_type(
    minimum: int | None = None,
    maximum: int | None = None
):

    # Factory validator function
    def validator(value):

        # Try to parse the value as an integer
        value = int(value)

        # Check if a minimum is set and if value falls short of the minimum
        if minimum is not None and value < minimum:

            # Raise an exception
            raise argparse.ArgumentTypeError(f"{value} is an invalid input value; it must be at least {minimum}!")

        # Check if a maximum is set and if the value exceeds the maximum
        if maximum is not None and value > maximum:

            # Raise an exception
            raise argparse.ArgumentTypeError(f"{value} is an invalid input value; it must be no more than {maximum}!")

        # Return constrained integer
        return value

    # Return the validator function
    return validator

# =================================================================================================
# argparse help message formatter class
# =================================================================================================
class HelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(
            prog,
            indent_increment=2,
            max_help_position=30,
            width=80,
        )

# =================================================================================================
# Get launch arguments
# =================================================================================================
def get_arguments() -> argparse.Namespace:

    # Initialize the argument parser
    parser = argparse.ArgumentParser(
        formatter_class = HelpFormatter,
        description = "A simple CLI tool that automatically downloads Bing's daily wallpaper.",
    )

    # Add image specific launch arguments
    image_group = parser.add_argument_group("Image options")

    image_group.add_argument(
        "--region",
        type = Region,
        choices = [region.value for region in Region],
        default = Region.EN_US,
        help = "Sets the server region from where the images are downloaded. The default value is en-US."
    )

    image_group.add_argument(
        "--day-index",
        type = int,
        choices = range(0, 8),
        default = 0,
        help = "Sets the starting day in the past from which images are downloaded. 0 represents today, 1 represents yesterday, 2 represents two days ago, and so on. Ignored when --daemon is set. The default value is 0."
    )

    image_group.add_argument(
        "--images",
        type = int,
        choices = range(1, 9),
        default = 1,
        help = "Sets the number of images that are downloaded. For example, 1 only downloads today's image, 2 downloads today's and yesterday's image, and so on. If --day-index is set to something different than 0, it will be N images downloaded starting from that day's index into the past. Ignored when --daemon is set. The default value is 1."
    )

    image_group.add_argument(
        "--resolution",
        type = Resolution,
        choices = [resolution.value for resolution in Resolution],
        default = Resolution.PIXEL_3840_2160,
        help = "Sets the native resolution of the downloaded image. The default value is UHD (3840 x 2160 pixels)."
    )

    image_group.add_argument(
        "--file-format",
        type = FileFormat,
        choices = [file_format.value for file_format in FileFormat],
        default = FileFormat.JPG,
        help = "Sets the image format of the downloaded image. The default value is jpg."
    )

    image_group.add_argument(
        "--download-directory",
        type = Path,
        metavar = "{path}",
        default = "./Downloads",
        help = "Sets the directory path where the images are downloaded to. The default value is './Downloads'."
    )

    image_group.add_argument(
        "--save-metadata",
        action="store_true",
        help = "Set this flag if the image metadata should be saved in an accompanying JSON file."
    )

    # Add logging specific launch arguments
    logging_group = parser.add_argument_group("Logging options")

    logging_group.add_argument(
        "--verbose",
        action="store_true",
        help = "Set this flag to enable the log output and get feedback messages."
    )

    logging_group.add_argument(
        "--log-file",
        type = Path,
        metavar = "{path}",
        default = None,
        help = "Sets the path of the log file. Only applies when --verbose is set. The default unset value will create no log file."
    )

    logging_group.add_argument(
        "--disable-escape-codes",
        action="store_true",
        help = "Set this flag to disable ANSI escape codes when logging to the terminal. This can help with terminals that don't support escape codes. Only applies when --verbose is set. The default unset value is to use escape codes."
    )

    # Add daemon specific launch arguments
    daemon_group = parser.add_argument_group("Daemon options")

    daemon_group.add_argument(
        "--daemon",
        action="store_true",
        help = "Set this flag to run continuously in daemon mode, repeatedly checking and downloading new images at the specified update interval until terminated."
    )

    daemon_group.add_argument(
        "--keep-images",
        type = constrained_integer_type(0, None),
        metavar = "{integer >= 0}",
        default = -1, # Any value < 0 = Keep all files
        help = "Sets the number of downloaded images to keep. If set to 0, it keeps no images; if set to 1, it keeps today's image; if set to 2, it keeps today's and yesterday's image, and so on. Only applies when --daemon is set. The default unset value is to keep all images."
    )

    daemon_group.add_argument(
        "--update-hours",
        type = constrained_integer_type(1, None),
        metavar = "{integer > 0}",
        default = 12,
        help = "Sets the number of hours in between update attempts. Only applies when --daemon is set. The default is 12 hours."
    )

    daemon_group.add_argument(
        "--update-failure-timeout-hours",
        type = constrained_integer_type(1, None),
        metavar = "{integer > 0}",
        default = 1,
        help = "Sets the number of hours to wait until the next update if the previous update failed. Only applies when --daemon is set. The default is 1 hour."
    )

    # Add request specific launch arguments
    request_group = parser.add_argument_group("Request options")

    request_group.add_argument(
        "--request-timeout-seconds",
        type = constrained_integer_type(1, None),
        metavar = "{integer > 0}",
        default = 10,
        help = "Sets the number of seconds before a request times out. The default value is 10 seconds."
    )

    request_group.add_argument(
        "--request-attempts",
        type = constrained_integer_type(1, None),
        metavar = "{integer > 0}",
        default = 10,
        help = "Sets the number of attempts before a request fails. The default value is 10."
    )

    request_group.add_argument(
        "--request-attempt-delay-seconds",
        type = constrained_integer_type(1, None),
        metavar = "{integer > 0}",
        default = 1,
        help = "Sets the number of seconds in between request attempts. The default is 1 second."
    )

    # Return the parsed arguments
    return parser.parse_args()