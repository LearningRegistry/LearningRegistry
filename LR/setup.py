try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='LR',
    version='0.1',
    description='',
    author='',
    author_email='',
    url='',
    install_requires=[
        "WebOb==1.1.1", "Pylons>=0.10", "pyparsing>=1.5.5", "restkit>=3.2.3",
        "couchdb>=0.8", "lxml>=2.3", "iso8601plus>=0.1.5", "ijson>=0.8.0",
        "pystache>=0.3.1", "PyJWT>=0.1.4", "Couchapp>=0.8.1", "uwsgi>=0.9.9"
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'lr': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'lr': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = lr.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
