# type: ignore

from pathlib import Path

from setuptools import find_packages, setup


LONG_DESCRIPTION = Path('README.md').read_text(encoding='utf-8')


setup(
    name='azafea',
    version='0.1.0',
    author='Mathieu Bridon',
    author_email='mathieu@endlessm.com',
    description='Process and store events',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/endlessm/azafea',
    packages=find_packages(),
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Database',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Typing :: Typed',
    ],
    python_requires='>=3.7',
)
