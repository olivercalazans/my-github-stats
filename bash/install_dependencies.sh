#!/bin/bash

# Install dependencies
apt update && apt install -y python3 python3-venv python3-pip

# Create virtual enviroment
python3 -m venv venv

# Init virtual enviroment
source ./venv/bin/activate

# Install python dependencies
pip install --upgrade pip
pip install -r requirements.txt
