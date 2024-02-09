from setuptools import setup, find_packages

setup(
    name='risibot-discord',
    version='0.0.1',
    url='https://github.com/Risitop/risibot-discord',
    author='Risitop',
    author_email='risitoppoe@gmail.com',
    description='A lightweight PoE-related Discord bot',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "discord", 
        "python-dotenv"
    ]
)