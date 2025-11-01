"""
Mirador: Local AI Orchestration Framework
Setup configuration for pip installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="mirador-ai",
    version="1.0.0",
    author="Matthew Scott",
    author_email="matthewdscott7@gmail.com",
    description="Local AI orchestration framework with multi-agent chaining for privacy-first workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guitargnarr/mirador",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "pyyaml>=6.0",
        "rich>=13.0",
        "click>=8.1.0",
        "requests>=2.31.0",
        "httpx>=0.25.0",
        "structlog>=23.0.0",
        "typer>=0.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
        "web": [
            "streamlit>=1.32.0",
            "plotly>=5.18.0",
        ],
        "full": [
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "sqlalchemy>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mirador=mirador.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "mirador": ["models/**/*.modelfile"],
    },
    zip_safe=False,
)
