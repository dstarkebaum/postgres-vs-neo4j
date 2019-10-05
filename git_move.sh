#!/bin/bash

git filter-branch --prune-empty --tree-filter '
git ls-tree --name-only $GIT_COMMIT | xargs -I create_tables.sh mv create_tables.sh postgres
'
