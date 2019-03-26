import setuptools


with open('README.md', 'r') as file_handle:
    long_description = file_handle.read()


setuptools.setup(
    name='pyprinttree',
    version='0.0.1.dev1',
    author='Tanner Netterville',
    author_email='tannern@gmail.com',
    description='A tool for printing tree structures to a console in a meaningful way.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=None,
    packages=setuptools.find_packages(),
    test_suite="pyprinttree.tests",
    tests_require=['psutil'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
