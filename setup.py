import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="HPCWatchdog",
    version="0.1.0",
    author="Brock Palen",
    author_email="brockp@umich.edu",
    description="Follow file changes in a folder to auto transfer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brockpalen/HPCWatchdog/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    scripts=["bin/hpc-watchdog"],
)
