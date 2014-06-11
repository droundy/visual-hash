#!/bin/bash

set -ev

# Here we will set up git hooks to do nice things...
if test -d git-scripts && test -d .git/hooks; then
    for i in `ls git-scripts | grep -v '~'`; do
        echo Setting up $i hook...
        ln -sf ../../git-scripts/$i .git/hooks/$i
    done
else
    echo We do not seem to be in a git repository.
fi
