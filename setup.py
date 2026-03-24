"""
Setup script for AI Content Creator
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-content-creator",
    version="1.0.0",
    author="AI Content Creator Team",
    description="Automated video clip generator and Facebook scheduler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "moviepy==1.0.3",
        "pillow>=10.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "schedule>=1.2.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-content-creator=main:main",
        ],
    },
)
