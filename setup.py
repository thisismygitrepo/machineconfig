
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="machineconfig",
    version="0.2",
    author="Alex Al-Saffar",
    author_email="programmer@usa.com",
    description="Dotfiles management package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thisismygitrepo/dofiles",
    project_urls={
        "Bug Tracker": "https://github.com/thisismygitrepo/machineconfig/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
)

# python setup.py sdist bdist_wheel
# twine upload dist/*

# the root directory belongs to gitrepo, it can have any name.
# the package name is dictated by 'name' field in setup.py file.
# the modules that are avilable after installation are the names under src directory, which can be different again.
# it is however good practice to unify all of the above.
