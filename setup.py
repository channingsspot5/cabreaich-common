# In cabreaich-common/setup.py
# Final version incorporating robust path handling

import os
from setuptools import setup, find_packages

# Get the absolute path to the directory containing setup.py
SETUP_DIR = os.path.abspath(os.path.dirname(__file__))

# Function to read the requirements file relative to setup.py
def read_requirements(filename="requirements.txt"):
    """Reads requirements from a file relative to setup.py"""
    # Construct the full path to the requirements file
    req_path = os.path.join(SETUP_DIR, filename)
    try:
        with open(req_path, 'r') as f:
            # Read lines, strip whitespace, ignore empty lines and comments
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"Warning: {filename} not found at {req_path}. No requirements loaded from file.")
        # Return an empty list if the file is not found
        return []

# Read version from version.py relative to setup.py
version = {}
# Construct path to version.py within the package directory, relative to setup.py
version_file = os.path.join(SETUP_DIR, 'cabreaich_common', 'version.py')
try:
    with open(version_file, 'r') as fp:
        exec(fp.read(), version)
except FileNotFoundError:
    print(f"Warning: version.py not found at {version_file}. Using default version '0.0.0'.")
    version['__version__'] = '0.0.0' # Default version if file not found

# Read README.md relative to setup.py
try:
    with open(os.path.join(SETUP_DIR, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    print(f"Warning: README.md not found at {SETUP_DIR}. Using empty long_description.")
    long_description = ''

# --- Main setup configuration ---
setup(
    name="cabreaich-common", # The name used for pip install
    version=version['__version__'], # Version read from version.py
    packages=find_packages(where=".", exclude=["tests*", "docs*"]), # Finds 'cabreaich_common/' directory
    description="Shared common library for the CabReAIch project.",
    long_description=long_description, # Content from README.md
    long_description_content_type='text/markdown', # Type of the long description
    author="ReAIch Team", # CHANGE THIS to your actual team/author name
    author_email="your.email@example.com", # CHANGE THIS to a relevant email
    # url="URL to your project repository (e.g., GitHub)", # Uncomment and add if desired
    install_requires=read_requirements(), # Dependencies read from requirements.txt
    python_requires='>=3.9', # Minimum Python version compatibility
    classifiers=[ # Standard PyPI classifiers (helps with searching/filtering)
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10", # Add versions you support
        "License :: OSI Approved :: MIT License", # Specify your license (consider SPDX format too)
        "Operating System :: OS Independent", # Should run on any OS
        "Development Status :: 3 - Alpha", # Or 4 - Beta, 5 - Production/Stable
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Private :: Do Not Upload", # Keep this if not intended for public PyPI
    ],
)