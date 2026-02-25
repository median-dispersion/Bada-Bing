from pathlib import Path
from enum import Enum
from datetime import datetime

# Logger properties
verbose: bool = False
disable_escape_codes: bool = False
file: Path | None = None

# =================================================================================================
# Log level enumerator
# =================================================================================================
class Level(str, Enum):

    LOG = "LOG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"

# =================================================================================================
# Escape code enumerator
# =================================================================================================
class EscapeCode(str, Enum):

    RESET = "\033[0m"
    BOLD = "\033[1m"
    GRAY = "\033[90m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"

# =================================================================================================
# Log a message
# =================================================================================================
def log(
    message: str,
    level: Level = Level.LOG
) -> None:

    # Check if verbose mode is enabled
    if verbose:

        # Get date and time of log message
        date = datetime.now().astimezone().isoformat()

        # Check if ANSI escape codes are disabled
        if disable_escape_codes:

            # Construct stream message
            stream_message = f"{date} [{level.value}] >> {message}"

        # If escape codes are enabled
        else:

            # Match color to log level
            match level:

                case Level.LOG: color = EscapeCode.MAGENTA
                case Level.INFO: color = EscapeCode.CYAN
                case Level.SUCCESS: color = EscapeCode.GREEN
                case Level.WARNING: color = EscapeCode.YELLOW
                case Level.ERROR: color = EscapeCode.RED

            # Construct stream message with escape codes
            stream_message = f"{EscapeCode.RESET.value}{EscapeCode.BLUE.value}{date}{EscapeCode.RESET.value} {EscapeCode.BLUE.value}{color.value}[{level.value}]{EscapeCode.RESET.value} {EscapeCode.GRAY.value}>>{EscapeCode.RESET.value} {message}"

        # Log message to terminal
        print(stream_message)

        # If message should be written to log file
        if file is not None:

            # Construct file message
            file_message = f"{date} [{level.value}] >> {message}\n"

            # Write message to log file
            with open(file, "a") as log_file: log_file.write(file_message)

# =================================================================================================
# Log methods
# =================================================================================================
def info(message: str) -> None: log(message, Level.INFO)
def success(message: str) -> None: log(message, Level.SUCCESS)
def warning(message: str) -> None: log(message, Level.WARNING)
def error(message: str) -> None: log(message, Level.ERROR)