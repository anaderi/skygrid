from setuptools import setup

setup(
    name='libscheduler',
    version='0.1.0',
    author='Yandex',
    author_email='sashab1@yandex-team.ru',
    packages=['libscheduler'],
    description='Metascheduler API library',
    install_requires=[
        "requests>=2.3.0"
    ],
)