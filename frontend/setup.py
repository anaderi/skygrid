from setuptools import setup, find_packages

setup(
    name='skygrid-frontend',
    version='0.1.0',
    url='https://github.com/anaderi/skygrid',
    author='Alexander Baranov',
    author_email='sashab1@yandex-team.ru',
    packages=find_packages(),
    description='SkyGrid server',
    install_requires=[
        "Flask==0.10.1",
        "Flask-WTF==0.10.3",
        "Jinja2==2.7.3",
        "MarkupSafe==0.23",
        "WTForms==2.0.1",
        "Werkzeug==0.9.6",
        "argparse==1.2.1",
        "itsdangerous==0.24",
        "requests==2.5.0",
        "skygrid-libscheduler==0.3.2",
        "skygrid-libskygrid==0.1.0",
        "wsgiref==0.1.2",
    ],
)