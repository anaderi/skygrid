from setuptools import setup, find_packages

setup(
    name='skygrid-metascheduler',
    version='0.1.0',
    url='https://github.com/anaderi/skygrid',
    author='Alexander Baranov',
    author_email='sashab1@yandex-team.ru',
    packages=['metascheduler', 'metascheduler.resources'],
    description='Metascheduler',
    install_requires=[
        "Flask==0.10.1",
        "Flask-RESTful==0.2.12",
        "Jinja2==2.7.3",
        "MarkupSafe==0.23",
        "WTForms==2.0.1",
        "Werkzeug==0.9.6",
        "aniso8601==0.83",
        "argparse==1.2.1",
        "flask-mongoengine==0.7.1",
        "itsdangerous==0.24",
        "mongoengine==0.8.7",
        "pymongo==2.7.2",
        "pytz==2014.4",
        "requests==2.3.0",
        "six==1.7.3",
        "wsgiref==0.1.2"
    ],
    tests_require=[
        "nose==1.3.4",
        "nose-testconfig==0.9",
    ],
)
