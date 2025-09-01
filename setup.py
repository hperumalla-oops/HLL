from setuptools import setup, find_packages

setup(
    name='hyperloglog',
    version='1.0',
    description='An implementation of HyperLogLog with sparse and dense modes',
    author='RV AIML Dep',
    packages=find_packages(),  
    install_requires=[
        'psycopg2==2.9.10', 'numpy==2.3.2', 'mmh3==5.2.0'
    ],
    python_requires='>=3.6',
)
