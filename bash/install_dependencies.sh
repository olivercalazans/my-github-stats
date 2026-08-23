#!/bin/bash

apt update && apt install -y python3-pip
pip install --upgrade pip
pip install -r requirements.txt