"""GRID_LRT: Grid LOFAR Tools"""
import sys
from subprocess import call, Popen, PIPE, STDOUT
if sys.version_info[0:2] != (2,6):
    from subprocess import check_output
import os
import socket
import git

__all__ = ["storage", 'auth', "application", "Staging", 'sandbox', 'Token']
__version__ = "0.5.0"
__author__ = "Alexandar P. Mechev"
__copyright__ = "2018 Alexandar P. Mechev"
__credits__ = ["Alexandar P. Mechev", "Natalie Danezi", "J.B.R. Oonk"]
__bibtex__ = """@misc{apmechev:2018,
      author       = {Alexandar P. Mechev} 
      title        = {apmechev/GRID_LRT: v0.5.0},
      month        = sep,
      year         = 2018,
      doi          = {10.5281/zenodo.1341127},
      url          = {https://doi.org/10.5281/zenodo.1341127}
    }"""
__license__ = "GPL 3.0"
__maintainer__ = "Alexandar P. Mechev"
__email__ = "LOFAR@apmechev.com"
__status__ = "Production"
__date__ = "2018-09-29"

if sys.version_info[0:2] == (2,6): 
    def check_output(*args, **kwargs):
        process = Popen(stdout=PIPE, *args, **kwargs)
        output, _ = process.communicate()
        return output


def format_version(version):
    fmt = '{tag}.{commitcount}+{gitsha}'
    parts = version.split('-')
    assert len(parts) in (3, 4)
    dirty = len(parts) == 4
    tag, count, sha = parts[:3]
    if count == '0' and not dirty:
        return tag
    return fmt.format(tag=tag, commitcount=count, gitsha=sha.lstrip('g'))

def get_git_version():
    repo = git.Repo(search_parent_directories=True)
    tag  = str(repo.tags[-1])
    return tag

def get_git_hash():
    git_hash = get_git_version()
    git_hash = git_hash.split(__version__+".")[1]
    return {'hash':git_hash.split('+')[1],
            'number of commits after '+__version__:git_hash.split('+')[0]}

#if socket.gethostname() != 'loui.grid.surfsara.nl':
#    RuntimeWarning("You're not running on loui. Some features will not work!")

if not call(["git", "branch"], stderr=STDOUT, stdout=open(os.devnull, 'w')) != 0:
    __commit__ = get_git_hash()
    __githash__ = __commit__['hash']
