#!/usr/bin/env python

# Use Seafile API to migrate libraries from version 2 to version 3.
# Steps:
# 1. Get library ID from input
# 2. Get library name, desc, and owner.
# 3. Create a new library, set name, desc and owner.
# 4. Copy stuffs from old library to new library.

import os
import stat
import sys
from seaserv import seafile_api

def count_files_recursive(repo_id, path='/'):
    num_files = 0
    for e in seafile_api.list_dir_by_path(repo_id, path):
        if stat.S_ISDIR(e.mode):
            num_files += count_files_recursive(repo_id,
                                               os.path.join(path, e.obj_name))
        else:
            num_files += 1
    return num_files

from_repo_id = sys.argv[1]
from_repo = seafile_api.get_repo(from_repo_id)
username = seafile_api.get_repo_owner(from_repo_id)
to_repo_id = seafile_api.create_repo(name=from_repo.name, desc=from_repo.desc,
                                     username=username, passwd=None)

dirents = seafile_api.list_dir_by_path(from_repo_id, '/')
for e in dirents:
    print "copying: " + e.obj_name
    obj_name = e.obj_name
    seafile_api.copy_file(from_repo_id, '/', obj_name, to_repo_id, '/',
                          obj_name, username, 0, 1)

print "*" * 60
print "OK, verifying..."
print "Origin library(%s): %d files. New Library(%s): %d files." % (
    from_repo_id[:8], count_files_recursive(from_repo_id),
    to_repo_id[:8], count_files_recursive(to_repo_id))
print "*" * 60

