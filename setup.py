#   Copyright © 2023 Achievement Unlocked Inc., dba CultureFoundry
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from setuptools import setup, find_packages

setup(
    name='foma_bindings',
    version='0.1.6',
    description='Python bindings for the foma finite-state technology suite',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/CultureFoundryCA/foma_bindings',
    author='CultureFoundry',
    author_email='info@culturefoundrystudios.com',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ],
    keywords=['foma', 'xfst', 'hfst', 'fst', 'fsm', 'mtfst', 'mtfsm'],
    packages=find_packages(include=['foma_bindings', 'foma_bindings.fst', 'foma_bindings.mtfst']),
    python_requires='>=3.10, <4',
)
