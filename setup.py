from setuptools import setup, find_packages

setup(
    name="newser-ai",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'feedparser>=6.0.10',
        'requests>=2.31.0',
        'python-telegram-bot>=20.5'
    ]
)
