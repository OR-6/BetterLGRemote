from setuptools import setup


LGTV_VERSION = '0.3'
LGTV_DOWNLOAD_URL = (
    'https://github.com/OR-6/BetterLGRemote/' + LGTV_VERSION
)

setup(
    name='LGTV',
    packages=['LGTV'],
    version=LGTV_VERSION,
    description='LG WebOS TV Controller.',
    long_description='',
    license='MIT',
    author='Numair Khan',
    author_email='ornor6@gmail.com',
    url='https://github.com/OR-6/BetterLGRemote',
    download_url=LGTV_DOWNLOAD_URL,
    entry_points={
        'console_scripts': [
            'lgtv=LGTV:main'
        ]
    },
    keywords=[
        'smarthome', 'smarttv', 'lg', 'tv', 'webos', 'remote'
    ],
    install_requires=[
        'wakeonlan',
        'ws4py',
        'requests',
        'getmac',
    ],
    data_files=[
        ('config', ['data/config.json'])
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Natural Language :: English',
    ],
)
