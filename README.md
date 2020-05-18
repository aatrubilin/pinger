[![GitHub last commit](https://img.shields.io/github/last-commit/aatrubilin/pinger.svg)](https://github.com/aatrubilin/pinger/commits/master)
[![License](https://img.shields.io/github/license/aatrubilin/pinger.svg)](LICENSE.md)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Pinger

This is a simple Python Flask application that pings `google.com` (by default) and show result in web graphs. 

## Note

- App is designed to use Postgres and run on Raspberry PI, 
  I assume it can run on other platforms and use other database technologies with basic modifications.
- Development was done on WinOS

## Getting Started

These instructions will get you a copy of the project up and running on your RPI.

### Setup Raspberry Pi

#### Install Raspbian Lite

_Raspbian is our official operating system for all models of the Raspberry Pi.
Use Raspberry Pi Imager for an easy way to install Raspbian and other 
operating systems to an SD card ready to use with your Raspberry Pi_
 
- [Raspberry Pi Imager for Windows](https://downloads.raspberrypi.org/imager/imager.exe)
- [Raspberry Pi Imager for macOS](https://downloads.raspberrypi.org/imager/imager.dmg)
- [Raspberry Pi Imager for Ubuntu](https://downloads.raspberrypi.org/imager/imager_amd64.deb)

Alternatively, use the link below:
[https://www.raspberrypi.org/downloads/](https://www.raspberrypi.org/downloads/)

#### Setup boot folder  

_In a basic Raspbian install, the boot files are stored on the first partition of the SD card, 
which is formatted with the FAT file system. 
This means that it can be read on Windows, macOS, and Linux devices._

_When the Raspberry Pi is powered on, it loads various files from the boot partition/folder 
in order to start up the various processors, then it boots the Linux kernel._

_More information at 
[https://www.raspberrypi.org/documentation/](https://www.raspberrypi.org/documentation/)_

- Add empty `ssh` file  enable SSH on boot.
- Add `wpa_supplicant.conf` file to boot folder to configure wifi on boot.

```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=RU

network={
    ssid="YOUR_WIFI_SID"
    psk="YOUR_FIFI_PASSWORD"
    key_mgmt=WPA-PSK
}
```

#### Setup Raspbian, optionally

- Connect to RPI via ssh, default login:pass - `pi:raspberry`
- Update packages `sudo apt-get update & sudo apt-get upgrade`
- Configure your Raspberry Pi `sudo raspi-config`

### Prerequisites

Install Docker

```bash 
curl -sSL https://get.docker.com | sh
```

Add permission to Pi User to run Docker Commands

```bash 
sudo usermod -aG docker pi
```

:exclamation: Reboot here or run the next commands with a sudo

Test Docker installation

```bash
docker run hello-world
```

Install proper dependencies

```bash
sudo apt-get install -y libffi-dev libssl-dev
sudo apt-get install -y python3 python3-pip
sudo apt-get remove python-configparser
```

Install Docker Compose

```bash
sudo pip3 install docker-compose
```

### Run app in docker

Clone the repo

```bash
git clone https://github.com/aatrubilin/pinger
```

Go to project path

```bash
cd pinger
```

Up docker compose

```bash
docker-compose up -d --build
```

Boom! :fire: It's done! Go to `http://{RPI IP}`

## Running the tests

Tests not ready yet...

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Development

Make sure to have the following on your host:

- [Python 3.7](https://www.python.org/downloads/)
- [PostgreSQL 10](https://www.postgresql.org/download/)

Clone the repo

```bash
git clone https://github.com/aatrubilin/pinger
```

Go to project path

```bash
cd pinger
```

Create a virtualenv:

```bash
python -m venv venv
```

Activate the virtualenv you have just created:

```bash
source venv/bin/activate
```

Install development requirements:

```bash
pip install -r requirements-dev.txt
```

Install pre-commit hooks

```bash
pre-commit install
```

Create a new PostgreSQL user and database:

```bash
sudo -u postgres psql
```

```postgresql
CREATE DATABASE pinger;
CREATE USER pinger WITH ENCRYPTED PASSWORD 'pinger';
GRANT ALL PRIVILEGES ON DATABASE pinger TO pinger;
```

Set the environment variables

```bash
export FLASK_ENV=development
export PING_HOSTS=google.com
export PING_DELAY_SEC=60
export PING_FAIL_DELAY_SEC=5
export DB_URL=postgresql://pinger:pinger@db/pinger
```

## Built With

* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - Python web microframework
* [Highcharts](https://www.highcharts.com/) - SVG-based, multi-platform charting library
* [Flatpickr](https://flatpickr.js.org/) - Javascript datetime picker
* [PostgreSQL 10](https://www.postgresql.org/) - Relational Database
* [Docker](https://docs.docker.com/) - App containerization

## Authors

* **Alexandr Trubilin** - *Initial work* - [AATrubilin](https://github.com/aatrubilin)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
