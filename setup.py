from setuptools import setup, find_packages

VERSION = '1.0.0'
DESCRIPTION = 'COMPOSITE multiplet detection'
LONG_DESCRIPTION = 'This is a multiplet detection tool for single cell data'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="sccomposite",
        version=VERSION,
        author="Haoran Hu",
        author_email="<hah112@pitt.edu>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that
        # needs to be installed along with your package. Eg: 'caer'

        keywords=['sccomposite', 'multiplet detection'],
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
