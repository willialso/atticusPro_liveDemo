#!/bin/bash
echo "==> Checking Python version"
python --version
python3 --version

echo "==> Upgrading pip and setuptools"
python -m pip install --upgrade pip==23.3.1
python -m pip install --upgrade setuptools==68.2.2
python -m pip install --upgrade wheel==0.41.2

echo "==> Installing requirements"
python -m pip install -r requirements.txt

echo "==> Build complete"
