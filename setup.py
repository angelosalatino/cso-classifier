import setuptools
import configparser

with open("README.md", "r") as fh:
    long_description = fh.read()

try:
    # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:
    # for pip <= 9.0.3
    from pip.req import parse_requirements

def load_requirements(fname):
    install_reqs = parse_requirements(fname, session=False)
    # Generator must be converted to list, or we will only have one chance to read each element, meaning that the first requirement will be skipped.
    install_reqs = list(install_reqs) 
    try:
        requirements = [str(ir.req) for ir in install_reqs]
    except:
        requirements = [str(ir.requirement) for ir in install_reqs]
    return requirements


# Import version number from version.py
config = configparser.ConfigParser()
config.read("cso_classifier/config.ini")
__version__ = config['classifier']['classifier_version']


setuptools.setup(
    name="cso-classifier",
    version=__version__,
    author="Angelo Salatino",
    author_email="angelo.salatino@open.ac.uk",
    description="A light-weight Python app for classifying scientific documents with the topics from the Computer Science Ontology (https://cso.kmi.open.ac.uk/home).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/angelosalatino/cso-classifier",
    packages=['cso_classifier'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_data = {'cso_classifier' : ['assets/*','config.ini'] },
    install_requires=load_requirements("requirements.txt"),
    python_requires='>=3.6.0',
)
