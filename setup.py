import setuptools

setuptools.setup(
    name='strats',
    version='0.0.1',
    packages=setuptools.find_packages(),
    install_requires=[
        "pytorch==1.10.2",
    ],
    url='https://github.com/jialuechen/strats',
    license='Apache 2.0',
    author='Jialue Chen',
    author_email='jialuechen@outlook.com',
    description='An Asynchronous and Event-driven Python Library for Algorithmic Trading'
)