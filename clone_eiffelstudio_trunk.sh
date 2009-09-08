#!/bin/sh

export OP=$1
export REPO_NAME=eiffelstudio-trunk-svn-git
export REPO_SVNURL=https://svn.eiffel.com/eiffelstudio
export CLONEGITSVN_STEP=50
export CLONEGITSVN_OPTIONS=" -T trunk -b branches -b tags --authors-file=/home/jfiat/trunk/svn.logs --ignore-paths=\"^[^/]+/(?:branches|tags)\" "
export CLONEGITSVN_FETCH_OPTIONS=" --ignore-paths=\"^[^/]+/(?:branches|tags)\" "

f_usage() {
echo Script
echo - init: initialize clone
echo - info: info about cloning
echo - fetch: fetch recent commits
echo - stop: stop cloning
echo - unstop: reset previous stop operation
echo - clean: clean previously stopped cloning
echo - reset: reset cloning i.e clobber
}

f_init() { 
	python clone-git-svn.py $REPO_NAME init $REPO_SVNURL 
}
f_fetch() {
	python clone-git-svn.py $REPO_NAME fetch 
}
f_info() {
	python clone-git-svn.py $REPO_NAME info 
}
f_stop() {
	python clone-git-svn.py $REPO_NAME stop 
}
f_unstop() {
	python clone-git-svn.py $REPO_NAME unstop 
}
f_clean() {
	python clone-git-svn.py $REPO_NAME clean 
}

f_reset() {
python clone-git-svn.py $REPO_NAME clean
\rm -rf ${REPO_NAME}*
}

if [ "$OP" = "" ]; then  
	f_usage 
fi

if [ "$OP" = "init" ]; then 
	f_init 
fi

if [ "$OP" = "info" ]; then 
	f_info 
fi

if [ "$OP" = "fetch" ]; then 
	f_fetch 
fi

if [ "$OP" = "stop" ]; then 
	f_stop 
fi

if [ "$OP" = "unstop" ]; then 
	f_unstop 
fi

if [ "$OP" = "clean" ]; then 
	f_clean 
fi

if [ "$OP" = "reset" ]; then 
	f_reset 
fi

