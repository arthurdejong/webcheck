from setuptools import setup, find_packages
setup(
    name = 'webcheck',
    version = '1.10.5a',
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'webcheck = webcheck.cmd:entry_point',
        ],
    },
    install_requires = ['setuptools', 'sqlalchemy'],
    extras_require = {
        'tidy': ['utidylib'],
        'soup': ['beautifulsoup'],
    },
    
    # metadata for pypi
    author = 'Arthur de Jong',
    author_email = 'arthur@arthurdejong.org',
    description = 'webcheck is a website checking tool for webmasters',
    license = 'GPL',
    keywords = 'spider',
    url = 'http://arthurdejong.org/webcheck/',
)
