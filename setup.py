from setuptools import setup, find_packages

setup(
    name='RMDupdater',
    version='0.01',
    packages=find_packages(),
    url='https://github.com/kittypr/RMDupdater',
    license='MIT',
    author='Julia Zhuk',
    author_email='julettazhuk@gmail.com',
    description='Script for detecting difference between local.md file and gdrivefile',
    install_requires=['oauth2client', 'google-api-python-client', 'httplib2']
)
