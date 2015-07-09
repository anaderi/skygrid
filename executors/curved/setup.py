from setuptools import setup, find_packages

setup(
    name='skygrid-docker-worker',
    version='0.3.14',
    url='https://github.com/anaderi/skygrid',
    author='Alexander Baranov',
    author_email='sashab1@yandex-team.ru',
    packages=find_packages(),
    description='SkyGrid docker worker',
    install_requires=[
        "lockfile==0.10.2",
        "requests>=2.5.1",
        "skygrid-libscheduler==0.5.2",
        "skygrid-libskygrid==0.1.1",
        "docker-py==1.1.0",
        "six==1.9.0",
        "websocket-client==0.26.0",
        "wsgiref==0.1.2",
        "easywebdav-dcache==1.2.1", # fixed easywebdav, see https://github.com/amnong/easywebdav/pull/37
    ],

    scripts = [
        'scripts/test-descriptor'
    ]
)
