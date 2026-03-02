# Bada Bing!

<a href="./LICENSE">
    <img alt="GitHub License" src="https://img.shields.io/github/license/median-dispersion/Bada-Bing?style=for-the-badge">
</a>

A simple CLI tool that automatically downloads Bing's daily wallpaper.

## 🕹️ Usage

The program can be started through your terminal of choice. You can configure the behavior via its launch options. To get a full list of launch options, add the `--help` argument or see the list below.
```bash
python main.py [--options]
```

### Options

#### Help
```
--help
```
Shows all available launch options and exits.

### Image options

#### Region
```
--region {de-DE,en-AU,en-CA,en-GB,en-IN,en-NZ,en-US,es-ES,fr-CA,fr-FR,it-IT,ja-JP,pt-BR,zh-CN}
```
Sets the server region from where the images are downloaded. The default value is en-US.

#### Day index
```
--day-index {0,1,2,3,4,5,6,7}
```
Sets the starting day in the past from which images are downloaded. 0 represents today, 1 represents yesterday, 2 represents two days ago, and so on. Ignored when --daemon is set. The default value is 0.

#### Number of images
```
--images {1,2,3,4,5,6,7,8}
```
Sets the number of images that are downloaded. For example, 1 only downloads today's image, 2 downloads today's and yesterday's image, and so on. If --day-index is set to something different than 0, it will be N images downloaded starting from that day's index into the past. Ignored when --daemon is set. The default value is 1.

#### Resolution
```
--resolution {UHD,1920x1200,1920x1080,1366x768,1280x768,1024x768,800x600,800x480,768x1280,720x1280,640x480,480x800,400x240,320x240,240x320}
```
Sets the native resolution of the downloaded image. The default value is UHD (3840 x 2160 pixels).

#### File format
```
--file-format {jpg,webp}
```
Sets the image format of the downloaded image. The default value is jpg.

#### Download directory
```
--download-directory {path}
```
Sets the directory path where the images are downloaded to. The default value is './Downloads'.

#### Save metadata
```
--save-metadata
```
Set this flag if the image metadata should be saved in an accompanying JSON file.

### Logging options

#### Verbose output
```
--verbose
```
Set this flag to enable the log output and get feedback messages.

#### Log file
```
--log-file {path}
```
Sets the path of the log file. Only applies when --verbose is set. The default unset value will create no log file.

#### Disable ANSI escape codes
```
--disable-escape-codes
```
Set this flag to disable ANSI escape codes when logging to the terminal. This can help with terminals that don't support escape codes. Only applies when --verbose is set. The default unset value is to use escape codes.

### Daemon options

#### Daemon mode
```
--daemon
```
Set this flag to run continuously in daemon mode, repeatedly checking and downloading new images at the specified update interval until terminated.

#### Number of images to keep
```
--keep-images {integer >= 0}
```
Sets the number of downloaded images to keep. If set to 0, it keeps no images; if set to 1, it keeps today's image; if set to 2, it keeps today's and yesterday's image, and so on. Only applies when --daemon is set. The default unset value is to keep all images.

#### Update interval
```
--update-hours {integer > 0}
```
Sets the number of hours in between update attempts. Only applies when --daemon is set. The default is 12 hours.

#### Update failure timeout
```
--update-failure-timeout-hours {integer > 0}
```
Sets the number of hours to wait until the next update if the previous update failed. Only applies when --daemon is set. The default is 1 hour.

### Request options

#### Request timeout
```
--request-timeout-seconds {integer > 0}
```
Sets the number of seconds before a request times out. The default value is 10 seconds.

#### Request attempts
```
--request-attempts {integer > 0}
```
Sets the number of attempts before a request fails. The default value is 10.

#### Request attempt delay
```
--request-attempt-delay-seconds {integer > 0}
```
Sets the number of seconds in between request attempts. The default is 1 second.

## 📋 Requirements

This tool requires the following dependencies:

- [Git](https://git-scm.com/)
- [Python 3+](https://www.python.org/)

### Install packages (Debian / Ubuntu)

```bash
sudo apt-get -y install git python3-full
```

### Install python dependencies

Create a new virtual Python environment inside the repository with:

```bash
python3 -m venv __venv__
```

Select the newly created virtual environment with:

```bash
source __venv__/bin/activate
```

Finally, install all Python dependencies inside the virtual environment with:

```bash
pip install -r requirements.txt
```