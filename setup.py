import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='spotifython',
    version='0.0.1.dev1',
    author='Niko Gupta',
    author_email='niko.gupta+spotifython@gmail.com',
    description='A Python library for interfacing with the Spotify REST api',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Guptacos/spotifython',
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    # Use ~= to signify that we aren't commiting to Python 4 support yet
    python_requires='~=3.6',
    project_urls={
        'Documentation': 'https://github.com/Guptacos/spotifython',
        'Source': 'https://github.com/Guptacos/spotifython',
        'Tracker': 'https://github.com/Guptacos/spotifython/issues',
    },
    install_requires=['requests'],
)
