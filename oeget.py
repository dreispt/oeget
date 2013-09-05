#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2013-08-16
@author: dreis
"""
import os
import sys
import shutil
import fnmatch
from pprint import pprint
import itertools


########
# Functional-style helpers

def getKey(dictionary, key):
    """Get key from dictionary, but don't fail if it's None"""
    return dictionary and dictionary.get(key)


def getFileLines(filename, filepath=None):
    """Get list of lines of a file"""
    with open(filepath and os.path.join(filepath, filename) or filename, 'r') as f:
            return(f.readlines())


def ls(path, match='*'):
    return [os.path.join(path, f)
            for f in os.listdir(path)
            if fnmatch.fnmatch(f, match)]


def listExtend(l1, l2):
    if l1:
        l1.extend(l2 or [])
    else:
        l1 = l2 or []
    return l1


def listAppend(l, x):
    if l:
        l.append(l)
    else:
        l = [x]
    return l


def listPopHead(l):
    x = l.pop(0)
    return (x, l)

########


def logMessage(logFlag, text):
    if logFlag:
        print(text)
    return True


def loadIndex(filepaths, log=False):
    if filepaths:
        filepath = filepaths.pop(0)
        data = eval('\n'.join(getFileLines(filepath)))
        #TODO: add localpath, reponame
        for x in data:
            dir = '.'.join( filepath.split('.')[:-1])
            x['localpath'] =  os.path.join(dir,
                    x['index_reponame'], x['index_name'])
        logMessage(log, '* Loaded %s: %s modules found.'
                        % (filepath, len(data)))
        listExtend(data, loadIndex(filepaths, log))
        return data


def loadIndexes(version, src, log=False):
    return loadIndex(ls(src, '*-%s.list' % version), log)


def getIndexDesc(index, module, log=False):
    for desc in index:
        if desc.get('index_name') == module:
            return desc


def getDepsList(index, module, acum_deps=None, log=False):
    desc = getIndexDesc(index, module)
    if desc:
        logMessage(log, "* %s => %s" % (module, desc.get('depends')))
        res = [module]
        acum_deps = acum_deps or []
        acum_deps.append(module)
        for dep in desc.get('depends'):
            if dep not in acum_deps:
               deps =getDepsList(index, dep, acum_deps, log=log)
               if deps:
                   res.extend(deps)
    else:
        if module != 'base':
            logMessage(log, '* ERROR: %s not found.' % module)
        res = None
    return res


def installModule(index, module, path, log=False):
    descs = [getIndexDesc(index, m, log=log)
            for m in getDepsList(index, module, log=log)]
    for m in descs:
        dest = os.path.join(path, m.get('index_name'))
        srcm = m.get('localpath')
        if not os.path.exists(dest):
            shutil.copytree(srcm, dest)
            #TODO: add metadata info
        else:
            pass #TODO: update


def download(url):
    """Copy the contents of a file from a given URL
    to a local file.
    """
    import urllib
    print("Downloading %s..." % url)
    webFile = urllib.urlopen(url)
    localFile = open(url.split('/')[-1], 'w')
    localFile.write(webFile.read())
    webFile.close()
    localFile.close()


### Main actions ###
def do_update(src='oeget.conf', to='./'):
    with open(src, 'r') as f:
        print("Using URL list in %s" % src)
        print("Storing indexes at %s" % to)
        for l in [x.strip() for x in f.readlines()]:
            if l:
                download(l)


if __name__ == "__main__":
    if False:
        index = loadIndexes('7.0', '/opt/openerp/src', log=True)
        pprint(len(index))
        pprint(
            getIndexDesc(index, 'mgmtsystem_nonconformity', log=True))
        pprint(
            getDepsList(index, 'mgmtsystem_nonconformity', log=False))

        #    pprint(
        #    getDeps(index, 'mgmtsystem_nonconformity', log=True))

    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        print("Usage: oebot [update|install <module>!upgrade]"
              " [--from=<list file>] [--to=<index dir>]")
    else:
        if sys.argv[1] == 'update':
            do_update()
        if sys.argv[1] == 'install':
            do_install(sys.argv[2])


