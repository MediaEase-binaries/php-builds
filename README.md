# PHP MediaEase Builds

This repository contains automated builds for PHP MediaEase, a custom PHP distribution optimized for MediaEase applications.

## Overview

PHP MediaEase is a custom PHP distribution that includes:
- Static PHP binary
- Essential PHP extensions
- Optimized configuration for MediaEase applications

## Features

- Automated builds via GitHub Actions
- Pre-compiled binaries ready to use
- Custom PHP configuration
- Regular updates with security patches

## Available Packages

The repository provides Debian packages (.deb) for various Ubuntu distributions. Each package includes:
- PHP binary with essential extensions
- Configuration files
- Documentation

## Installation

### Manual Installation
1. Download the appropriate .deb package for your system
2. Install using: `sudo dpkg -i package_name.deb`
3. Fix any dependencies if needed: `sudo apt-get install -f`

## Build Process

The build process is automated using GitHub Actions and includes:
1. Downloading the base PHP static binary
2. Customizing the PHP configuration
3. Creating a Debian package
4. Publishing a GitHub release

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
