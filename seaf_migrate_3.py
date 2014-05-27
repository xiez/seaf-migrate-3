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
from seaserv import seafile_api, get_group_repos_by_owner, \
    list_inner_pub_repos_by_owner

def count_files_recursive(repo_id, path='/'):
    num_files = 0
    for e in seafile_api.list_dir_by_path(repo_id, path):
        if stat.S_ISDIR(e.mode):
            num_files += count_files_recursive(repo_id,
                                               os.path.join(path, e.obj_name))
        else:
            num_files += 1
    return num_files

origin_repo_id = sys.argv[1]
origin_repo = seafile_api.get_repo(origin_repo_id)
username = seafile_api.get_repo_owner(origin_repo_id)
new_repo_id = seafile_api.create_repo(name=origin_repo.name,
                                      desc=origin_repo.desc,
                                      username=username, passwd=None)

dirents = seafile_api.list_dir_by_path(origin_repo_id, '/')
for e in dirents:
    print "copying: " + e.obj_name
    obj_name = e.obj_name
    seafile_api.copy_file(origin_repo_id, '/', obj_name, new_repo_id, '/',
                          obj_name, username, 0, 1)

print "*" * 60
print "OK, verifying..."
print "Origin library(%s): %d files. New Library(%s): %d files." % (
    origin_repo_id[:8], count_files_recursive(origin_repo_id),
    new_repo_id[:8], count_files_recursive(new_repo_id))
print "*" * 60

#get the share info of the origin repo
#used for share the new repo
shared_repos = []
shared_repos += seafile_api.get_share_out_repo_list(username, -1, -1)
shared_repos += get_group_repos_by_owner(username)
shared_repos += list_inner_pub_repos_by_owner(username)
for repo in shared_repos:
    if repo.repo_id != origin_repo_id:
        continue

    if repo.share_type == "personal":
        # @username share this repo to 'repo.user'
        print "Share %s-%s to user %s with permission %s" % (
            new_repo_id[:8], repo.repo_name, repo.user, repo.permission)
        seafile_api.share_repo(new_repo_id, username, repo.user,
                               repo.permission)

    if repo.share_type == "group":
        # @username share this repo to group
        print "Share %s-%s to group %d with permission %s" % (
            new_repo_id[:8], repo.repo_name, repo.group_id, repo.permission)
        seafile_api.group_share_repo(new_repo_id, repo.group_id, username,
                                     repo.permission)

    if repo.share_type == "public":
        print "Share %s-%s to public with permission %s" % (
            new_repo_id[:8], repo.repo_name, repo.permission)
        seafile_api.add_inner_pub_repo(new_repo_id, repo.permission)

print "*" * 60
print "OK, successfully shared new library to users/groups/public"
print "*" * 60
