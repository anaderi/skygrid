from setuptools import setup, find_packages

setup(
    name='yacern-tokenmanager',
    version='0.1.0',
    url='https://github.com/anaderi/skygrid',
    author='Alexander Baranov',
    author_email='sashab1@yandex-team.ru',
    packages=find_packages(),
    description='Token manager for Yandex/CERN projects',
    install_requires=[
        "Flask==0.10.1",
        "Jinja2==2.7.3",
        "MarkupSafe==0.23",
        "Werkzeug==0.10.4",
        "itsdangerous==0.24",
        "redis==2.10.3",
        "wsgiref==0.1.2",
    ],
    include_package_data=True
)
