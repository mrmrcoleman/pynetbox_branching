from setuptools import setup, find_packages

setup(
    name="pynetbox-branching",
    version="0.1.0",
    author="Mark Coleman",
    author_email="mrmrcoleman@gmail.com",
    description="A Python library for managing NetBox branches and interacting with NetBox Branches with pynetbox",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mrmrcoleman/pynetbox-branching",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)