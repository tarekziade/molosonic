from setuptools import setup, find_packages


install_requires = ['molotov', 'arsenic']
description = ''

for file_ in ('README', 'CHANGELOG'):
    with open('%s.rst' % file_) as f:
        description += f.read() + '\n\n'


classifiers = ["Programming Language :: Python",
               "License :: OSI Approved :: Apache Software License",
               "Development Status :: 1 - Planning"]


setup(name='molosonic',
      version='0.1',
      url='https://github.com/loads/molosonic',
      packages=find_packages(),
      long_description=description.strip(),
      description=("Spiffy load testing tool."),
      author="Tarek Ziade",
      author_email="tarek@ziade.org",
      include_package_data=True,
      zip_safe=False,
      classifiers=classifiers,
      install_requires=install_requires)
