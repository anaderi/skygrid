from setuptools import setup
setup(
    name='skygrid-ms-cli',
    version='0.1',
    py_modules=['mscli'],
    include_package_data=True,
    install_requires=[
        'Click',
        'libscheduler'
    ],
    entry_points='''
        [console_scripts]
        mscli=mscli:cli
    ''',
)