REF: http://svn.collab.net/repos/svn/trunk/notes/svnsync.txt
                           ==== What Is It? ====

svnsync is a tool for creating and maintaining read-only mirrors of
subversion repositories.  It works by replaying commits that occurred
in one repository and committing it into another.

                           ==== Basic Setup ====

First, you need to create your destination repository:

$ svnadmin create dest

Because svnsync uses revprops to keep track of bookkeeping information
(and because it copies revprops from the source to the destination)
it needs to be able to change revprops on your destination repository.
To do this you'll need to set up a pre-revprop-change hook script that
lets the user you'll run svnsync as make arbitrary propchanges.

$ cat <<'EOF' > dest/hooks/pre-revprop-change
#!/bin/sh
USER="$3"

if [ "$USER" = "svnsync" ]; then exit 0; fi

echo "Only the svnsync user can change revprops" >&2
exit 1
EOF
$ chmod +x dest/hooks/pre-revprop-change

$ svnsync init --username svnsync file://`pwd`/dest \
                                  http://svn.example.org/source/repos
Copied properties for revision 0
$

Note that the arguments to 'svnsync init' are two arbitrary repository
URLs.  The first is the destination, which must be empty, and the second
is the source.

Now you can just run the 'svnsync sync' command to synchronize pending
revisions.  This will copy any revisions that exist in the source repos
but don't exist in the destination repos.

$ svnsync sync file://`pwd`/dest
Committed revision 1.
Copied properties for revision 1.
Committed revision 2.
Copied properties for revision 2.
Committed revision 3.
Copied properties for revision 3.
...

                              ==== Locks ====

If you kill a sync while it's occurring there's a chance that it might
leave the repository "locked".  svnsync ensures that only one svnsync
process is copying data into a given destination repository at a time
by creating a svn:sync-lock revprop on revision zero of the destination
repository.  If that property is there, but you're sure no svnsync is
actually running, you can unlock the repository by deleting that revprop.

$ svn pdel --revprop -r 0 svn:sync-lock file://`pwd`/dest

                               ==== FAQ ====

