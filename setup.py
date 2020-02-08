from setuptools import setup, find_packages

INSTALL_REQUIREMENTS = [
    "numpy==1.18.1",
    "numba==0.48.0"
]

setup(
    name='vlapy',
    version='1.0',
    packages=find_packages(),
    url='',
    license='MIT',
    author='Archis Joglekar',
    author_email='archisj@gmail.com',
    description='Spectral 1D-1V Vlasov-Fokker-Planck code',
    install_requires=INSTALL_REQUIREMENTS,
    include_package_data=True,
)
