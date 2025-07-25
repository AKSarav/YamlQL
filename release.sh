#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Pre-flight Checks ---
echo "--- Running pre-flight checks ---"

# Check for required tools. We only need python, as we'll run tools as modules.
command -v python >/dev/null 2>&1 || { echo >&2 "I require 'python' but it's not installed. Aborting."; exit 1; }

# Check for PyPI API Token in environment variables
# PyPI now requires API tokens for uploads. See https://pypi.org/help/#apitoken
if [ -z "$PYPI_API_TOKEN" ]; then
    echo >&2 "Error: PyPI API Token is not set."
    echo >&2 "Please generate a token on PyPI and set it as an environment variable:"
    echo >&2 "  export PYPI_API_TOKEN='pypi-your-token-here'"
    exit 1
fi

echo "--- Pre-flight checks passed ---"

# --- Build ---
echo "--- Building the package ---"

# Clean up previous builds
echo "Cleaning up old builds from dist/..."
rm -rf dist/*

# Build the source and wheel distributions using 'python -m build'
echo "Building source and wheel distributions..."
python -m build

echo "--- Build complete ---"

# --- Upload to PyPI ---
echo "--- Uploading to PyPI ---"

# Upload using 'python -m twine' with a PyPI API Token.
# The username is '__token__' when using an API token.
python -m twine upload dist/* --username "__token__" --password "$PYPI_API_TOKEN"

echo "--- Upload complete ---"
echo "--- Successfully released new version to PyPI! ---" 