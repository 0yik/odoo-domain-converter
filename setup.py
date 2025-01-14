from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="odoo-domain-converter",
    version="0.1.0",
    author="Anang Ajirahmawan",
    author_email="aji.abuismail@gmail.com",
    description="Convert human-readable expressions to Odoo domain format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0yik/odoo-domain-converter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    install_requires=[
        "odoorpc>=0.9.0",
    ],
    entry_points={
        'console_scripts': [
            'odoo-domain-converter=odoo_domain_converter.cli:main',
        ],
    },
)
