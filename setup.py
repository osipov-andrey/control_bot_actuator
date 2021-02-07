"""
Control-bot actuator (CBA)
Каркас для создания командных интерфейсов для телеграм-ботов
"""

from setuptools import find_packages, setup


module_name = 'cba'

setup(
    name=module_name,
    version='0.0.1',
    author='Andrey Osipov',
    author_email='developer.osipov@gmail.com',
    description=__file__.__doc__,
    url='',
    platforms='all',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: Russian',
        'Operating System :: Win10',
        'Operating System :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    python_requires='>=3.7',
    install_requires=[
        'PyYAML==5.3.1',
        'beautifulsoup4==4.9.3',
        'httpx==0.14.3',
        'aioamqp==0.14.0',
    ],
    extras_require={
        'dev': [
            'pydantic==1.7.3',
            'pytest==6.2.2',
            'pytest-asyncio==0.14.0',
            'pytest-mock==3.5.1',
        ],
    },
    packages=find_packages(exclude=['tests']),

    include_package_data=True
)
