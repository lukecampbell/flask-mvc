#!/usr/bin/env python
'''
@author Luke Campbell
@file flask_mvc/utils/generate.py
@license Apache 2.0
'''
import cjson as json
import os
import sys
import pkg_resources

def generate(project_root, project_name, template_file):
    '''
    Generate a new project based on the JSON schema
    '''
    print 'Initializing new project %s at %s' %(project_name,project_root)
    print 'Using template: %s' % os.path.basename(template_file)
    if not os.path.exists(project_root):
        os.mkdir(project_root)
    if template_file.endswith('.json'):
        template = {}
        with open(template_file,'r') as f:
            template = json.decode(f.read())
            generate_walk(project_root, project_name, template['files'])

def generate_walk(dirent, name, template):
    '''
    Walk the template object creating the appropriate files
    '''
    if not isinstance(template,dict):
        return
    for k,v in template.iteritems():
        if '%s' in k:
            k = k.replace('%s', name)
        path = os.path.join(dirent,k)
        if isinstance(v,dict):
            print 'Creating ', path
            if not os.path.exists(path):
                os.mkdir(path)
            generate_walk(path, name, v)
        else:
            print 'Writing  ',path
            with open(os.path.join(dirent,k),'w') as f:
                if '%s' in v:
                    v = v.replace('%s',name)
                f.write(v)
def main():
    if len(sys.argv) < 3:
        print '%s <project name> <project root> [<template>]' % sys.argv[0]
        sys.exit(1)

    name = sys.argv[1]
    root = sys.argv[2]
    if len(sys.argv) > 3:
        template = sys.argv[3]
    else:
        template = os.path.join(pkg_resources.resource_filename(__name__, 'templates/empty.json'))
    generate(root,name,template)


if __name__ == '__main__':
    main()
