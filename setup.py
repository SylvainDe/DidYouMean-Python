from distutils.core import setup
# with the help from http://peterdowns.com/posts/first-time-with-pypi.html
setup(
    name='didyoumean',
    packages=['didyoumean'],  # this must be the same as the name above
    version='0.1',
    description=('Logic to have suggestions in case of errors '
                 '(NameError, AttributeError, etc).'),
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
        'typo'],
    classifiers=[],
)
