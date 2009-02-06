#!/usr/bin/python

import sys;
import os;
from string import atoi;

step = 500

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

def print_info(a,rev=0):
	if rev == 0:
		print ("Info for [%s]" % (a))
		os.system ("tail -n 4 %s/.git/svn/.metadata" % (a))
	else:
		print ("Info for [%s-%d]" % (a,rev))
		os.system ("tail -n 4 %s-%d/svn/.metadata" % (a,rev))

def logthis(a_folder,msg):
	lf = open ("%s-log" % (a_folder), 'a+');
	lf.write ("%s\n" % (msg))
	lf.close()


a = sys.argv[1]
if len(sys.argv) > 2:
	if sys.argv[2] == "info":
		print_info(a)
		sys.exit()
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
		os.system ("cat %s-%d/svn/.metadata" % (a,rev))

		if os.path.exists ("%s-%d" % (a, rev)):
			os.system ("rm -rf %s/.git" % (a))
			os.system ("cp -rf %s-%d %s/.git" % (a, rev, a))
		else:
			print ("Cleaning ... unsafe")
		os.system ("\\rm -rf %s-stop" % (a))
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
		os.system ("mv %s-%d %s-backup" % (a, rev, a))
		os.system ("cp -rf %s/.git %s-%d" % (a, a, i))
		os.system ("echo %d > %s-last" % (i,a))
	else:
		do_stop()

sys.exit()
