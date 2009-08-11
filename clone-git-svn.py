#!/usr/bin/python

import sys;
import os;
from string import atoi,strip;
import re;

if os.environ.has_key ('CLONEGITSVN_STEP'):
	step = atoi(os.environ['CLONEGITSVN_STEP'])
else:
	step = 500

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

def last_rev(a_folder):
	try:
		f = open ("%s-last" % (a_folder), 'r');
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

def stop_requested(a_folder):
	return os.path.exists ("%s-stop" %(a_folder))

def do_stop():
	print ("Stop requested!!!")
	sys.exit(3)

def ensure_backup(a_folder):
	if not os.path.exists ("%s-backup" %(a_folder)):
		os.mkdir ("%s-backup" % (a_folder))

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
		res = "%s%s\n" % (res, l_lines[i])
	return res


def get_svn_head_revision (a_repo_url):
	try:
		f = os.popen ("svn info %s" % (a_repo_url), 'r')
		l_lines = re.split ("\n", f.read())
		f.close()
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
		s = os.path.join (a_id, ".git", "svn", ".metadata")
	else:
		s = os.path.join ("%s-%d" % (a_id, a_rev), ".git", "svn", ".metadata")
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
		print ("Info for [%s]" % (a))
		s = tail (git_metadata_filename (a), 4)
		print s
	else:
		print ("Info for [%s-%d]" % (a,rev))
		s = tail (git_metadata_filename (a,rev), 4)
		print s

def logthis(a_folder,msg):
	lf = open ("%s-log" % (a_folder), 'a+');
	lf.write ("%s\n" % (msg))
	lf.close()


repo_url = ""
a = sys.argv[1]
if len(sys.argv) > 2:
	if sys.argv[2] == "info":
		print_info(a)
		sys.exit()
	elif sys.argv[2] == "init":
		repo_url = sys.argv[3]
		os.system ("mkdir %s" % (a))
		os.system ("git svn init %s --stdlayout -R svn %s" % (repo_url, a))
		print_info(a)
	elif sys.argv[2] == "fetch":
		print_info(a)
		if len (sys.argv) > 3:
			step = atoi (sys.argv[3])
	elif sys.argv[2] == "stop":
		os.system ("echo stop > %s-stop" % (a))
		print ("Requesting stop for %s" % (a))
		print_info(a)
		sys.exit()
	elif sys.argv[2] == "clean":
		print_info(a)
		if len (sys.argv) > 3:
			rev = atoi (sys.argv[3])
		else:
			rev = last_rev(a)
		print_info(a,rev)
		os.system ("%s %s" % (cat_cmd, git_metadata_filename(a,rev)))

		if os.path.exists ("%s-%d" % (a, rev)):
			os.system ("%s %s" % (rmdir_cmd, os.path.join (a,'.git')))
			os.system ("%s %s-%d %s" % (cpdir_cmd, a, rev, os.path.join (a,'.git')))
		else:
			print ("Cleaning ... unsafe")
		os.system ("%s %s-stop" % (rm_cmd, a))
		sys.exit()
	else:
		sys.exit()
else:
	print_info(a)

d = os.getcwd()
i = 0
stop = stop_requested(a)
if stop:
	do_stop()
ensure_backup(a);

repo_last_rev = get_last_fetched_rev(a)

if repo_url == "":
	repo_url = get_info(a, "reposRoot")
head_rev = get_svn_head_revision (repo_url)
print "svn URL=%s" %(repo_url)
print "svn HEAD=%d" %(head_rev)
print "last svn fetched=%d" %(repo_last_rev)

while not stop:
	rev = repo_last_rev
	i = rev + step
	stop = head_rev > 0 and i >= head_rev
	if stop:
		cmd = "git svn fetch -r BASE:%d " % ('head_rev')
	else:
		cmd = "git svn fetch -r BASE:%d " % (i)

	repo_last_rev = get_last_fetched_rev(a)

	logthis(a,cmd)
	sys.stdout.write ("%s\n" % (cmd))
	os.chdir (a)
	os.system (cmd)
	os.chdir (d)
	if not stop:
		stop = stop_requested(a)
		if not stop:
			ensure_backup(a);
			rev = last_rev(a)
			if rev > 0:
				print "Backing up %s-%d to %s-backup" % (a,rev, a)
				os.system ("%s %s-%d %s-backup" % (mv_cmd, a, rev, a))
			os.system ("%s %s %s-%d" % (cpdir_cmd, os.path.join (a, '.git'), a, repo_last_rev))
			os.system ("echo %d > %s-last" % (repo_last_rev,a))
		else:
			do_stop()

sys.exit()
