from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.1.0'
DESCRIPTION = 'Aerodiode device control'
LONG_DESCRIPTION = 'Enables to control Aerodiode optoelectronic device website : https://www.aerodiode.com/'

# Setting up
setup(
    name="aerodiode",
    version=VERSION,
    author="AeroDIODE",
    author_email="<info@AeroDIODE.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['pyserial', 'csv-reader'],
    keywords=['python', 'optoelectronic', 'laser', 'aerodiode'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
   
)
