import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class TestCommand_(TestCommand):
    def finalize_options(self):
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


def get_git_version():
    from subprocess import check_output
    return check_output(('git', 'describe', '--match', '[0-9].*')).strip()


def parse_requirements(filename):
    with open(filename) as f:
        for line in f:
            if not line.startswith('git+'):
                yield line.strip()


setup(
    name='wonder-common',
    version=get_git_version(),
    author="Wonder Place Ltd",
    author_email="developers@wonderpl.com",
    description="Common/shared python web services code",
    long_description=open('README.md').read(),
    license='Copyright 2014 Wonder Place Ltd',
    url='https://github.com/rockpack/wonder-common',
    zip_safe=False,
    packages=find_packages(exclude=['test']),
    include_package_data=True,
    install_requires=list(parse_requirements('requirements.txt')),
    tests_require=list(parse_requirements('requirements-dev.txt')),
    setup_requires=['setuptools_git'],
    cmdclass={
        'test': TestCommand_,
    },
)
