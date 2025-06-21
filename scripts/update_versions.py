#!/usr/bin/env python3

import os
import re
import sys
import yaml
import requests
from typing import Dict, List, Set, Optional
from datetime import datetime
from pathlib import Path

STATIC_PHP_URL = "https://dl.static-php.dev/static-php-cli/bulk/"
VERSION_FILE = Path(__file__).parent.parent / "php-static-versions.yaml"

# Default extensions and libraries for all PHP versions
DEFAULT_EXTENSIONS = "apcu,bcmath,bz2,calendar,ctype,curl,dba,dom,event,exif,fileinfo,filter,ftp,gd,gmp,iconv,imagick,imap,intl,mbregex,mbstring,mysqli,mysqlnd,opcache,openssl,pcntl,pdo,pdo_mysql,pgsql,phar,posix,protobuf,readline,redis,session,shmop,simplexml,soap,sockets,sodium,sqlite3,swoole,swoole-hook-mysql,swoole-hook-pgsql,swoole-hook-sqlite,sysvmsg,sysvsem,sysvshm,tokenizer,xml,xmlreader,xmlwriter,xsl,zip,zlib"
DEFAULT_LIBS = "pkg-config,lib-base,bzip2,zlib,openssl,brotli,libiconv,icu,libxml2,nghttp2,libcares,curl,libevent,libpng,libwebp,libjpeg,freetype,gmp,libtiff,libde265,libaom,libheif,libzip,imagemagick,imap,onig,ncurses,readline,libxslt,libsodium,postgresql,sqlite"

def get_available_versions() -> Dict[str, Set[str]]:
    """
    Fetch available versions from static-php.dev and group them by major.minor version
    Returns a dict where key is major.minor and value is a set of full version numbers
    """
    response = requests.get(STATIC_PHP_URL)
    if response.status_code != 200:
        print(f"Error fetching versions: {response.status_code}")
        sys.exit(1)

    versions: Dict[str, Set[str]] = {}
    pattern = r'php-(\d+\.\d+\.\d+)-(cli|fpm)-linux-x86_64\.tar\.gz'
    
    # Group versions by their components (cli/fpm)
    components: Dict[str, Set[str]] = {'cli': set(), 'fpm': set()}
    for filename in response.text.splitlines():
        match = re.search(pattern, filename)
        if match:
            version, component = match.groups()
            components[component].add(version)

    # Only keep versions that have both CLI and FPM
    complete_versions = components['cli'].intersection(components['fpm'])
    
    # Group by major.minor
    for version in complete_versions:
        major_minor = '.'.join(version.split('.')[:2])
        if major_minor not in versions:
            versions[major_minor] = set()
        versions[major_minor].add(version)

    return versions

def get_latest_versions(versions: Dict[str, Set[str]]) -> List[Dict[str, str]]:
    """
    Get the latest version for each major.minor and format them with extensions and libs
    Excludes PHP 8.0.x versions
    """
    latest_versions = []
    for major_minor, version_set in versions.items():
        # Skip PHP 8.0.x versions
        if major_minor == "8.0":
            continue
        latest = sorted(version_set, key=lambda x: [int(i) for i in x.split('.')])[-1]
        latest_versions.append({
            'version': latest,
            'major': major_minor,
            'extensions': DEFAULT_EXTENSIONS,
            'libs': DEFAULT_LIBS
        })
    return sorted(latest_versions, key=lambda x: x['version'])

def load_current_versions() -> dict:
    """
    Load current versions from YAML file
    """
    if not VERSION_FILE.exists():
        return {'php_static_versions': {'include': []}}
    
    with open(VERSION_FILE) as f:
        return yaml.safe_load(f)

def get_version_data(version_list: List[dict], version: str) -> Optional[dict]:
    """
    Get existing version data from the current list if it exists
    """
    for v in version_list:
        if v['version'] == version:
            return v
    return None

def update_versions_file(latest_versions: List[Dict[str, str]]) -> None:
    """
    Update the YAML file with new versions while preserving existing configuration
    """
    current_data = load_current_versions()
    current_versions = current_data.get('php_static_versions', {}).get('include', [])
    
    # Prepare new version list while preserving existing configuration
    new_versions = []
    for version_info in latest_versions:
        existing_data = get_version_data(current_versions, version_info['version'])
        if existing_data:
            # Preserve existing configuration
            new_versions.append(existing_data)
        else:
            # Add new version with default configuration
            new_versions.append(version_info)
            print(f"Added new version: {version_info['version']}")

    # Check for removed versions
    current_version_numbers = {v['version'] for v in current_versions}
    new_version_numbers = {v['version'] for v in latest_versions}
    removed = current_version_numbers - new_version_numbers
    if removed:
        print(f"Removed versions: {', '.join(sorted(removed))}")

    # Update the file
    data = {
        'php_static_versions': {
            'include': new_versions
        }
    }

    # Create parent directory if it doesn't exist
    VERSION_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(VERSION_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

def main():
    print("Fetching available PHP versions...")
    versions = get_available_versions()
    latest_versions = get_latest_versions(versions)
    
    print("\nFound latest versions:")
    for version in latest_versions:
        print(f"- {version['version']} (PHP {version['major']})")
    
    print("\nUpdating versions file...")
    update_versions_file(latest_versions)
    print(f"\nVersion file updated: {VERSION_FILE}")

if __name__ == "__main__":
    main() 
