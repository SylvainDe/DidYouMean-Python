"""Setup."""

try:
        from setuptools import setup
except ImportError:
        from distutils.core import setup
# with the help from http://peterdowns.com/posts/first-time-with-pypi.html
# http://www.scotttorborg.com/python-packaging/minimal.html
setup(
    name='BetterErrorMessages',
    packages=['didyoumean'],
    version='0.4',
    description=('Logic to have suggestions in case of errors '
                 '(NameError, AttributeError, ImportError, TypeError, etc).'),
    author='Sylvain Desodt',
    author_email='sylvain.desodt+didyoumean@gmail.com',
    url='https://github.com/SylvainDe/DidYouMean-Python',
    download_url='https://github.com/SylvainDe/DidYouMean-Python/tarball/0.1',
    keywords=[
        'didyoumean',
        'exception',
        'error',
        'suggestion',
        'excepthook',
        'decorator',
        'contextmanager',
        'typo'],
    classifiers=[],
)
