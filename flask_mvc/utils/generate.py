#!/usr/bin/env python
import cjson as json
import os

def generate(project_root, project_name, template_file):
    if not os.path.exists(project_root):
        os.mkdir(project_root)
    template = {}
    with open(template_file,'r') as f:
        template = json.decode(f.read())
        generate_walk(project_root, project_name, template['files'])

def generate_walk(dirent, name, template):
    if not isinstance(template,dict):
        return
    for k,v in template.iteritems():
        if '%s' in k:
            print "named"
            k = k % name
        if isinstance(v,dict):
            print 'Subdir ', k
            if not os.path.exists(os.path.join(dirent,k)):
                os.mkdir(os.path.join(dirent,k))
            generate_walk(os.path.join(dirent,k), name, v)
        else:
            print 'Writing ', k
            with open(os.path.join(dirent,k),'w') as f:
                f.write(v)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print 'generate <project name> <project root> [<template>]'
        sys.exit(1)

    name = sys.argv[1]
    root = sys.argv[2]
    if len(sys.argv) > 3:
        template = sys.argv[3]
    else:
        template = os.path.join(os.path.dirname(__file__), 'templates/empty.json')
    generate(root,name,template)

    
