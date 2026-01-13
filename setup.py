import io
import os
import setuptools
import configparser

# --- Long description (robust UTF-8, fallback if README missing) ---
readme = ""
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with io.open(readme_path, "r", encoding="utf-8") as fh:
        readme = fh.read()
else:
    readme = "CSO Classifier: classify scientific documents with topics from the Computer Science Ontology."



requirements_to_install = [
    'igraph==0.10.4',
    'gensim==4.3.3',
    'click==7.1.2',
    'hurry.filesize==0.9',
    'kneed==0.3.1',
    'nltk==3.6.2',
    'rapidfuzz==2.11.1',
    'numpy>=1.19.5',
    'requests==2.25.1',
    'spacy==3.0.5',
    'strsimpy==0.2.0',
    'update-checker==0.18.0'
]


# --- Version from config.ini (UTF-8 read) ---
config = configparser.ConfigParser()
config.read(os.path.join("cso_classifier", "config.ini"), encoding="utf-8")
__version__ = config["classifier"]["classifier_version"]


setuptools.setup(
    name="cso-classifier",
    version=__version__,
    author="Angelo Salatino",
    author_email="angelo.salatino@open.ac.uk",
    description="A light-weight Python app for classifying scientific documents with the topics from the Computer Science Ontology (https://cso.kmi.open.ac.uk/home).",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/angelosalatino/cso-classifier",
    packages=['cso_classifier'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_data = {'cso_classifier' : ['assets/*','config.ini'] },
    install_requires=requirements_to_install,
    license="Apache-2.0",
    python_requires='>=3.11.0',
)