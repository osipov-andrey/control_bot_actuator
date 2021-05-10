"""
Control-bot actuator (CBA)
Framework for creating command interfaces for control bot
"""

from setuptools import find_packages, setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


MODULE_NAME = "cba"

setup(
    name=MODULE_NAME,
    version="2.0.0",
    author="Andrey Osipov",
    author_email="developer.osipov@gmail.com",
    description="Framework for creating command interfaces for control bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/osipov-andrey/control_bot_actuator",
    platforms="all",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyYAML==5.3.1",
        "beautifulsoup4==4.9.3",
        "httpx==0.14.3",
        "aioamqp==0.14.0",
    ],
    extras_require={
        "dev": [
            "pydantic==1.7.3",
            "pytest==6.2.2",
            "pytest-asyncio==0.14.0",
            "pytest-mock==3.5.1",
            "black~=20.8b1",
        ],
    },
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=["tests"]),
    include_package_data=True,
)
