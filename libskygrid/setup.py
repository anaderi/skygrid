from setuptools import setup

setup(
    name='skygrid-libskygrid',
    version='0.1.1',
    url='https://github.com/anaderi/skygrid',
    author='Alexander Baranov',
    author_email='sashab1@yandex-team.ru',
    description='SkyGrid API library',
    packages=['libskygrid'],
    install_requires=[
        "requests>=2.3.0",
    ],
    tests_require=[
        "nose==1.3.4",
        "nose-testconfig==0.9",
    ],
)
