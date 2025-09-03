"""
Setup script for md2html package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="dober-md2html",
    version="2.0.0",
    author="Bean Raid",
    author_email="",
    description="A powerful, theme-based Markdown to HTML converter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dober-wow/dober-md-html",
    packages=find_packages(),
    package_data={
        'md2html': ['themes/*.css'],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: Markdown",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "markdown>=3.0",
        "beautifulsoup4>=4.9",
        "click>=8.0",
        "watchdog>=2.0",
        "aiohttp>=3.8",
    ],
    entry_points={
        'console_scripts': [
            'md2html=md2html.cli:cli',
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/dober-wow/dober-md-html/issues",
        "Source": "https://github.com/dober-wow/dober-md-html",
    },
)