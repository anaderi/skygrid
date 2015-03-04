from setuptools import setup, find_packages

setup(
    name='skygrid-docker-worker',
    version='0.1',
    url='https://github.com/anaderi/skygrid',
    author='Alexander Baranov',
    author_email='sashab1@yandex-team.ru',
    packages=find_packages(),
    description='SkyGrid docker worker',
    install_requires=[
        "lockfile==0.10.2",
        "requests==2.5.1",
        "skygrid-libscheduler==0.3.3",
        "skygrid-libskygrid==0.1.1",
    ],
)
