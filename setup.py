import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


install_requires = [
    'dnx-mysql-replication==0.21'
    # 'awswrangler-git @ https://github.com/awslabs/aws-data-wrangler/releases/download/1.5.0/awswrangler-layer-1.5.0-py3.8.zip#egg=awswrangler-git-1.5.0'
]

setuptools.setup(
    name='dnx-data',  # Replace with your own username
    version='0.2.3',
    author='DNX Solutions',
    author_email='contact@dnx.solutions',
    description='DNX data solution package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/DNXLabs/dnx-data',
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
