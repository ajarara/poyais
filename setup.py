from setuptools import setup

setup(
    name='Poyais',
    version='0.0.1',
    description=('Dynamite, with a laser beam.')
    url='https://github.com/alphor/python-poyais',
    author='Ahmad Jarara',
    author_email='ajarara94@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Super-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        ],
    keywords='',
    packages=['poyais'],
    extras_require={
        'test': ['pytest', 'hypothesis'],
    },
)
