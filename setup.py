from setuptools import setup, find_packages

setup(
    name="newser-ai",
    version="0.3",
    packages=find_packages(),
    install_requires=[
        'requests>=2.31.0',
        'python-telegram-bot>=20.5',
        'openai>=1.6.1',
        'SQLAlchemy>=2.0.25',
        'pydantic-settings>=2.8.1',
        'pydantic>=2.7.1',
        'beautifulsoup4>=4.12.3'
    ]
)
