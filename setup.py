from setuptools import setup, find_packages

setup(
    name="data_automation_bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "requests",
        "sqlalchemy",
        "python-dotenv",
        "schedule",
        "matplotlib",
        "seaborn",
    ],
    author="Messo Francis",
    author_email="mesofrancis@outlook.com",
    description="A Python-based bot to automate data preprocessing and reporting",
    keywords="data automation, preprocessing, reporting, API integration",
    python_requires=">=3.8",
)
