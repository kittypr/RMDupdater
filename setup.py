from setuptools import setup, find_packages

setup(
    name='RMDupdater',
    version='0.0.4',
    packages=find_packages(),
    url='https://github.com/kittypr/RMDupdater',
    license='MIT',
    author='Julia Zhuk',
    author_email='julettazhuk@gmail.com',
    description='Script for detecting difference between local.md file and gdrivefile',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],

    install_requires=['oauth2client', 'google-api-python-client', 'httplib2'],
    scripts=['RMDupdater/RMD_updater.py', 'RMDupdater/RMD_updater_create_token.py']
)
