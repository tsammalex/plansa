from setuptools import setup, find_packages


setup(
    name='plansa',
    version='0.0',
    description='plansa',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'clld>=8',  # >=7.0
        'pytsammalex[clld]',
        'clld-glottologfamily-plugin>=4.0',
        'pyglottolog',
        'clldmpg>=4.2',

],
extras_require={
        'dev': ['flake8', 'waitress', 'psycopg2'],
        'test': [
            'mock',
            'pytest>=5.4',
            'pytest-clld',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
            'selenium',
            'zope.component>=3.11.0',
        ],
    },
    test_suite="plansa",
    entry_points="""\
    [paste.app_factory]
    main = plansa:main
""")
