import os
import sys
import json

os.environ['PIP_PYTHON_PATH'] = sys.executable

for _dir in ('vendor', 'patched', '..'):
    dirpath = os.path.sep.join([os.path.dirname(__file__), _dir])
    sys.path.insert(0, dirpath)

import pipenv.utils
import pipenv.core
import requests
from requests_html import HTMLSession
from docopt import docopt
from pip.req import InstallRequirement

class Resolver(object):
    """The Pipenv super–resolver."""

    def __init__(self, sources, project, verbose=False):
        super(Resolver, self).__init__()
        self.sources = sources
        self.project = project
        self.verbose = verbose
        self.session = HTMLSession()
        self.unresolved = {}
        self.resolved = {}

    def __iter__(self):
        for package_name, package in self.unresolved.copy().items():
            del self.unresolved[package_name]
            yield package_name, package

    def register(self, package):
        self.unresolved.update(package)

    def fetch_versions(self, package_name, source):
        url = '{0}/{1}'.format(source['url'], pipenv.utils.pep423_name(package_name))
        versions = set()

        r = self.session.get(url)
        for link in r.html.absolute_links:
            version = link.split('-')[1].split('#')[0]
            for extension in ('.tar.gz', '.win', '.win32', '.zip'):
                version = version.replace(extension, '')

            versions.add(version)

        return versions




    def graph(self):
        for package_name, package_version in self:
            for source in self.sources:
                versions = self.fetch_versions(package_name, source)


            print(package_name, package_version)


            # self.resolved[package_name] = self.unresolved[package_name]



        return self.resolved


def which(*args, **kwargs):
    return sys.executable

project = pipenv.core.project

resolver = Resolver(sources=project.sources, project=project)

def resolve(packages, pre, sources, verbose=False, clear=False):
    packages = [pipenv.utils.convert_deps_from_pip(package) for package in packages]

    for package in packages:
        resolver.register(package)

    return resolver.graph()

    # return pipenv.utils.resolve_deps(packages, which, project=project, pre=pre, sources=sources, clear=clear, verbose=verbose)

if __name__ == '__main__':

    is_verbose = '--verbose' in sys.argv
    do_pre = '--pre' in sys.argv
    do_clear = '--clear' in sys.argv
    if 'PIPENV_PACKAGES' in os.environ:
        packages = os.environ['PIPENV_PACKAGES'].strip().split('\n')
    else:
        packages = sys.argv[1:]

        for i, package in enumerate(packages):
            if package.startswith('--'):
                del packages[i]

    results = resolve(packages, pre=do_pre, sources=project.sources, verbose=is_verbose, clear=do_clear)


    print('RESULTS:')

    if results:
        print(json.dumps(results))
    else:
        print(json.dumps([]))
