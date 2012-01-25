from setuptools import setup, find_packages

setup(
    name = 'Should',
    version = '1.4.1',
    packages = find_packages(),

    install_requires = [ ],

    # testing
    test_suite = 'nose.collector',
    tests_require = [
        'nose==1.1.2',
    ],
    
    # metadata for PyPi and others
    author = 'Brian Hicks',
    author_email = 'brian@brianthicks.com',
    description = 'Task Management from the Command Line',
    license = 'TODO',
    url = 'https://github.com/BrianHicks/should',
    download_url = 'https://github.com/BrianHicks/should',
    scripts = ['should/bin/should.py'],

    long_description = open('README.md').read(),
)
