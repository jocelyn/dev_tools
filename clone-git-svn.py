#!/usr/bin/python

import sys;
import os;
from string import atoi,strip;
import re;

git_cmd = "git"
svn_cmd = "svn"
backup_enabled = 0


### Feature declaration ###
def output(m):
	global repo_id
	print (m)

def execute_cmd(a_cmd, a_msg="", exit_on_error=0):
	global repo_id
	import subprocess ;
	output ( "Execute: %s \n" % (a_cmd) )

	r = 0
	retcode = 0
	err = ""
	try:
		retcode = subprocess.call(a_cmd,0, None, None, sys.stdout, sys.stderr, shell=True)
		r = retcode
		if retcode < 0:
			r = -retcode
			err = "Command was terminated by signal (retcode=%d)" %(-retcode)
			output ( "%s\n" % (err) )
		#else: output ( "Command returned (retcode=%d)" %(-retcode) )
	except OSError, e:
		r = -1
		err = "Execution failed: %s" % (e)
		output ( "%s\n" % (err) )
	except:
		r = -1
		err = "Execution interrupted"
		output ( "%s\n" % (err) )

	if r:
		if len(a_msg) > 0:
			if r == -1:
				output ( ("Error occurred (%s)\n", err) )
			else:
				output ("Error: %s (%s error=%d: %s)\n"%(a_msg, err, r, os.strerror (r)))
			if exit_on_error == 1:
				logthis(os.getcwd(), "Exit on Error (%s)" % (err))
				#logthis(os.getcwd(), "Exit on Error (%s) cmd=%s" % (err, a_cmd))
				sys.exit()
	return r

def last_rev(a_folder):
	try:
		f = open (lastrev_path (a_folder), 'r');
		l = f.readline()
		f.close()
	except:
		l = "0";

	i = 0
	try:
		i = atoi(l)
	except:
		i = 0
	return i

def get_step(a_folder):
	global step
	try:
		fn = step_path (a_folder);
		if os.path.exists (fn):
			f = open (step_path (a_folder), 'r');
			l = f.readline()
			f.close()
			step = atoi(l)
		else:
			set_step (a_folder, step)
	except:
		set_step (a_folder, step)

def set_step(a_folder, n):
	try:
		f = open (step_path (a_folder), 'w');
		f.write("%d\n" % (n))
		f.close()
	except:
		output ( "Error while writing to file %s" % (step_path (a_folder)) )
		sys.exit()

def stop_requested(a_folder):
	return os.path.exists (stop_path (a_folder))

def do_stop():
	output ("Stop requested!!!")
	sys.exit(3)

def ensure_tmp_folder(a_folder):
	s = tmp_folder (a_folder)
	if not os.path.exists (s):
		os.makedirs (s)

def ensure_backup(a_folder):
	s = backup_path (a_folder)
	if not os.path.exists (s):
		os.makedirs (s)

def tail(a_fn, n=4):
	import re;
	try:
		f = open (a_fn, 'r');
		l_lines = re.split ("\n", f.read())
		f.close()
	except:
		l_lines = []

	l_count = len(l_lines)
	l_lower = l_count - n - 1
	if l_lower < 0:
		l_lower = 0
	l_upper = l_count
	res = ""
	for i in range(l_lower, l_upper):
		if len(l_lines[i]) > 0:
			res = "%s%s\n" % (res, l_lines[i])
	return res


def get_svn_head_revision (a_repo_url):
	global svn_cmd
	try:
		f = os.popen ("%s info %s" % (svn_cmd, a_repo_url), 'r')
		l_lines = re.split ("\n", f.read())
		r = f.close()
		if r:
			output ( "Error while getting HEAD of %s (error=%d)" % (a_repo_url, r) )
	except:
		l_lines = []

	for l in l_lines:
		l = strip(l)
		vals = l.split (":", 2)
		if len(vals) >= 2:
			k = strip (vals[0])
			if k == "Revision":
				return atoi( strip (vals[1]))
	return -1

def git_metadata_field_value(a_id, a_field):
	l_fn = git_metadata_filename(a_id)
	try:
		f = open (l_fn, 'r');
		l_lines = re.split ("\n", f.read())
		f.close()
	except:
		l_lines = []

	for l in l_lines:
		l = strip(l)
		vals = l.split ("=", 2)
		if len(vals) >= 2:
			k = strip (vals[0])
			if k == a_field:
				return strip (vals[1])
	return ""

def git_metadata_filename(a_id,a_rev=0):
	if a_rev == 0:
		s = os.path.join (repo_folder (a_id), ".git", "svn", ".metadata")
	else:
		s = os.path.join (repo_rev_folder (a_id, a_rev), ".git", "svn", ".metadata")
	return s

def get_info(a,a_field):
	return git_metadata_field_value(a, a_field)

def get_last_fetched_rev(a):
	l_rev = get_info(a, "branches-maxRev")
	try:
		res =  atoi(l_rev)
	except: 
		res = 0
	return res

def print_info(a,rev=0):
	if rev == 0:
		s = tail (git_metadata_filename (a), 4)
		get_step(a)
		output ("Info for [%s] step=%d" % (a, step))
		output ( "  %s" % (s) )
		if stop_requested(a):
			output ( " - Stop requested" )
	else:
		output ("Info for [%s_%d]" % (a,rev))
		s = tail (git_metadata_filename (a,rev), 4)
		output ( s )

def repo_folder(a):
	return os.path.join ("repo", a)
def tmp_folder(a):
	return os.path.join ("repo", "%s-tmp" % (a))
def log_path(a):
	return os.path.join (tmp_folder(a),"log")
def backup_path(a):
	return os.path.join (tmp_folder(a),"backup")
def repo_rev_folder(a,a_rev):
	return os.path.join (tmp_folder (a),"_%d" %(a_rev))
def stop_path(a):
	return os.path.join (tmp_folder(a),"stop")
def lastrev_path(a):
	return os.path.join (tmp_folder(a),"lastrev")
def step_path(a):
	return os.path.join (tmp_folder(a),"step")

def logthis(a_folder,msg):
	lf = open (log_path(a_folder), 'a+');
	lf.write ("%s\n" % (msg))
	lf.close()


###############################################
### MAIN ######################################
###############################################

global repo_id
repo_id = sys.argv[1]

sys.stdout = open("%s.out" % (os.path.join ("repo", repo_id)),"a+")
sys.stderr = open("%s.err" % (os.path.join ("repo", repo_id)),"a+")

is_windows = sys.platform == 'win32'

if is_windows:
	cat_cmd = "type"
	mv_cmd = "move"
	rmdir_cmd = "rd /q/s"
	rm_cmd = "del"
	cpdir_cmd = "xcopy /I /E /Y /Q"
else:
	cat_cmd = "cat"
	mv_cmd = "mv"
	rmdir_cmd = "\\rm -rf"
	rm_cmd = "\\rm -f"
	cpdir_cmd = "cp -rf"


if os.environ.has_key ('CLONEGITSVN_STEP'):
	step = atoi(os.environ['CLONEGITSVN_STEP'])
else:
	step = 50
repo_url = ""
ensure_tmp_folder(repo_id)
get_step(repo_id)
if len(sys.argv) > 2:
	if sys.argv[2] == "info":
		print_info(repo_id)
		sys.exit()
	elif sys.argv[2] == "init":
		repo_url = sys.argv[3]
		os.makedirs (repo_folder (repo_id))
		if os.environ.has_key ('CLONEGITSVN_OPTIONS'):
			extra_options = os.environ['CLONEGITSVN_OPTIONS']
		else:
			extra_options = " --stdlayout "
		cmd = "%s svn init %s %s -R svn %s" % (git_cmd, repo_url, extra_options, repo_folder(repo_id))
		output ( cmd )
		execute_cmd(cmd, "'init' failed", 1)
		print_info(repo_id)
		sys.exit()
	elif sys.argv[2] == "fetch":
		print_info(repo_id)
		if len (sys.argv) > 3:
			step = atoi (sys.argv[3])
	elif sys.argv[2] == "stop":
		os.system ("echo stop > %s" % (stop_path (repo_id)))
		output ("Requesting stop for %s" % (repo_id))
		print_info(repo_id)
		sys.exit()
	elif sys.argv[2] == "unstop":
		print_info(repo_id)
		os.system ("%s %s" % (rm_cmd, stop_path (repo_id)))
		sys.exit()
	elif sys.argv[2] == "clean":
		print_info(repo_id)
		if len (sys.argv) > 3:
			rev = atoi (sys.argv[3])
		else:
			rev = last_rev(repo_id)
		print_info(repo_id,rev)
		os.system ("%s %s" % (cat_cmd, git_metadata_filename(repo_id,rev)))

		if os.path.exists (repo_rev_folder (repo_id, rev)):
			os.system ("%s %s" % (rmdir_cmd, os.path.join (repo_folder(repo_id),'.git')))
			os.system ("%s %s %s" % (cpdir_cmd, ackup_rev_path (repo_id, rev), os.path.join (repo_folder(repo_id),'.git')))
		else:
			output ("Cleaning ... unsafe")
		os.system ("%s %s" % (rm_cmd, stop_path (repo_id)))
		sys.exit()
	else:
		sys.exit()
else:
	print_info(repo_id)

d = os.getcwd()
i = 0
stop = stop_requested(repo_id)
if stop:
	do_stop()
ensure_backup(repo_id);

repo_last_rev = get_last_fetched_rev(repo_id)

if repo_url == "":
	repo_url = get_info(repo_id, "reposRoot")
head_rev = get_svn_head_revision (repo_url)
output ( "svn URL=%s" %(repo_url) )
output ( "svn HEAD=%d" %(head_rev) )
output ( "last svn fetched=%d" %(repo_last_rev) )

fetch_extra_options = ""
if os.environ.has_key ('CLONEGITSVN_FETCH_OPTIONS'):
	fetch_extra_options = os.environ['CLONEGITSVN_FETCH_OPTIONS']

while not stop:
	get_step(repo_id)
	i = repo_last_rev + step
	stop = head_rev > 0 and i >= head_rev
	if stop:
		cmd = "%s svn fetch %s -r BASE:%d " % (git_cmd, fetch_extra_options, head_rev)
	else:
		cmd = "%s svn fetch %s -r BASE:%d " % (git_cmd, fetch_extra_options, i)


	logthis(repo_id,cmd)
	sys.stdout.write ("%s\n" % (cmd))
	os.chdir (repo_folder(repo_id))
	fetch_retcode = execute_cmd(cmd, "'fetch' failed, exit now" , 1)

	execute_cmd("%s gc" % (git_cmd), "git gc failed, ignore" , 0)
	os.chdir (d)

	repo_last_rev = get_last_fetched_rev(repo_id)

	if not stop:
		stop = stop_requested(repo_id)
		if not stop:
			ensure_backup(repo_id);
			rev = last_rev(repo_id)
			if rev > 0:
				if backup_enabled:
					output ( "Backing up %s to %s" % (repo_rev_folder (repo_id, rev), backup_path (repo_id)) )
					execute_cmd ("%s %s %s" % (mv_cmd, repo_rev_folder(repo_id, rev), backup_path (repo_id)), "backup failed")
				else:
					execute_cmd ("%s %s" % (rmdir_cmd, repo_rev_folder(repo_id, rev)), "Repo [%d] removal failed" % (rev))
			execute_cmd ("%s %s %s" % (cpdir_cmd, os.path.join (repo_folder(repo_id), '.git'), repo_rev_folder (repo_id, repo_last_rev)), "keep current repo failed")

			## record last rev fetched
			os.system ("echo %d > %s" % (repo_last_rev, lastrev_path (repo_id)))
		else:
			do_stop()

sys.stdout.close()
sys.stderr.close()

sys.exit()
