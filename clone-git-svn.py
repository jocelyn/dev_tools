#!/usr/bin/python

import sys;
import os;
from string import atoi;

step = 50
is_windows = sys.platform == 'win32'

if is_windows:
	cat_cmd = "type"
	mv_cmd = "move"
	rmdir_cmd = "rd /q/s"
	cpdir_cmd = "xcopy /I /E /Y "
else:
	cat_cmd = "cat"
	mv_cmd = "mv"
	rmdir_cmd = "\\rm -rf"
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
	try:
		f = open (a_fn, 'r');
		l_lines = re.split ("\n", f.read())
		f.close()
	except:
		l_lines = []

	l_count = len(l_lines)
	l_lower = l_count - n
	if l_lower <= 0:
		l_lower = 1
	l_upper = l_count
	res = ""
	for i in range(l_lower, l_upper):
		res = "%s%s\n" % (res, l_lines[i])
	return res

def git_metadata_filename(a_id,a_rev=0):
	if is_windows:
		if rev == 0:
			s = "%s\\.git\\svn\\.metadata" % (a_id)
		else:
			s = "%s-%d\\.git\\svn\\.metadata" % (a_id, a_rev)
	else:
		if rev == 0:
			s = "%s/.git/svn/.metadata" % (a_id)
		else:
			s = "%s-%d/.git/svn/.metadata" % (a_id, a_rev)
	return s

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


a = sys.argv[1]
if len(sys.argv) > 2:
	if sys.argv[2] == "info":
		print_info(a)
		sys.exit()
	elif sys.argv[2] == "init":
		os.system ("mkdir %s" % (a))
		os.system ("git svn init %s --stdlayout -R svn %s" % (sys.argv[3], a))
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
			os.system ("%s %s/.git" % (rmdir_cmd, a))
			os.system ("%s %s-%d %s/.git" % (cpdir_cmd, a, rev, a))
		else:
			print ("Cleaning ... unsafe")
		os.system ("%s %s-stop" % (rmdir_cmd, a))
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

while (i < 79000) and not stop:
	rev = last_rev(a)
	i = rev + step
	cmd = "git svn fetch -r BASE:%d " % (i)
	logthis(a,cmd)
	sys.stdout.write ("%s\n" % (cmd))
	os.chdir (a)
	os.system (cmd)
	os.chdir (d)
	stop = stop_requested(a)
	if not stop:
		ensure_backup(a);
		os.system ("%s %s-%d %s-backup" % (mv_cmd, a, rev, a))
		os.system ("%s %s/.git %s-%d" % (cpdir_cmd, a, a, i))
		os.system ("echo %d > %s-last" % (i,a))
	else:
		do_stop()

sys.exit()
