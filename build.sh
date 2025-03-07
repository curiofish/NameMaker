#!/bin/bash

# Install system dependencies
apt-get update
apt-get install -y python3-dev python3-pip python3-venv

# Install Python packages
pip install -r requirements.txt 