@echo off
setlocal
set OP=%1
set REPO_NAME=gobo-svn-git
export REPO_SVNURL=https://gobo-eiffel.svn.sourceforge.net/svnroot/gobo-eiffel/gobo
set CLONEGITSVN_STEP=500

if .%OP%. == .. goto usage
if .%OP%. == .init. goto init
if .%OP%. == .info. goto info
if .%OP%. == .fetch. goto fetch
if .%OP%. == .stop. goto stop
if .%OP%. == .clean. goto clean
if .%OP%. == .reset. goto reset
goto usage

:usage
echo Script
echo - init: initialize clone
echo - info: info about cloning
echo - fetch: fetch recent commits
echo - stop: stop cloning
echo - clean: clean previously stopped cloning
echo - reset: reset cloning i.e clobber
goto end

:init
clone-git-svn.py %REPO_NAME% init %REPO_SVNURL%
goto end

:fetch
clone-git-svn.py %REPO_NAME% fetch
goto end

:info
clone-git-svn.py %REPO_NAME% info
goto end

:stop
clone-git-svn.py %REPO_NAME% stop
goto end

:clean
clone-git-svn.py %REPO_NAME% clean
goto end

:reset
clone-git-svn.py %REPO_NAME% clean
rd /q/s %REPO_NAME%
rd /q/s %REPO_NAME%-backup
del %REPO_NAME%*
goto end


:end
endlocal
