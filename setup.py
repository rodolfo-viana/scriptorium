from setuptools import setup, find_packages

setup(
    name="scriptorium",
    version="0.1.0",
    description="Advanced logging package with asynchronous, context-aware logging",
    author="Rodolfo Viana",
    author_email="eu@rodolfoviana.com.br",
    url="https://github.com/rodolfo-viana/scriptorium",
    packages=find_packages(),
    install_requires=[
        "rich>=13.0",
    ],
    extras_require={
        "dev": ["pytest>=8.0", "black>=25.0", "flake8>=7.0", "mypy>=1.14"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Logging",
    ],
    python_requires=">=3.7",
    test_suite="tests"
)
