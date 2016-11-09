# ------------------------------------------------------------------------------------------------
# Script name: backup.py
# Created on: 2016.11.05
# Updated:    2016.11.07
# Author: Hayden Elza
# Purpose: 	Used to backup multiple files or directories into bz2 archives.
#			A breif log file is kept to track potential errors.
#			Emails are sent to notify sys admin of errors immediately.
# Version: 2.1
# History: - Rewrote the script to be more effiecent and archive over network instead of copying
#            locally first.
#          - Using tarfile to archive instead of shutil.make_archive, this allows the compression
#            of a list of files rather than a directory
#          - Using config file to easily modify different applications.
# -------------------------------------------------------------------------------------------------

import os
import sys
import datetime
import shutil


# Load config
import main_config
nosp_name        = main_config.nosp_name
full_name        = main_config.full_name
to_backup        = main_config.to_backup
temp_directory   = main_config.temp_directory  # Can be None to archive directly to output dir
output_directory = main_config.output_directory


def archive(files,base_name,workspace,nosp_name,datestamp):
	import tarfile

	print "Archiving..."

	# Build archive name
	archive_name = nosp_name + "_" + datestamp
	
	if workspace is None:
		shutil.make_archive(base_name+archive_name, "bztar", root_dir)
		print "Finished archiving."
	else:
		tar = tarfile.open(workspace+archive_name+".tar.bz2", "w:bz2")

		for file in files: tar.add(file)
		tar.close()

		print datetime_stamp("timestamp"),"Finished archiving."
		shutil.move(workspace+archive_name+".tar.bz2", base_name+archive_name+".tar.bz2")
		print datetime_stamp("timestamp"),"Finished copying"
		os.rmdir(workspace)
		print datetime_stamp("timestamp"),"Removed workspace"

def send_email(msg,full_name):
	import smtplib
	import email_config

	# Set message parameters
	gmail_user = email_config.user
	gmail_pwd  = email_config.pwd
	FROM       = main_config.fro
	TO         = main_config.to
	SUBJECT    = full_name

	# Prepare actual message
	message = """From: {}\n, To: {}\nSubject: {}\n\n{}""".format(FROM, TO, SUBJECT, msg)

	# Send message
	try:
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.ehlo()
		server.starttls()
		server.login(gmail_user, gmail_pwd)
		server.sendmail(FROM, TO, message)
		server.close()
		print "Successfully sent email."
	except:
		print "Failed to send email."

def datetime_stamp(stamp_type):
	t = datetime.datetime.now()
	if   stamp_type == "datestamp": return "{}-{:02}-{:02}".format(t.year,t.month,t.day)
	elif stamp_type == "timestamp": return "{}-{:02}-{:02} {:02}.{:02}".format(t.year,t.month,t.day,t.hour,t.minute)
	else: return

warnings = []
datestamp = datetime_stamp("datestamp")

# Set sys.stdout to write to log (psst, reset for stdout at end of script)
logFile = nosp_name + "_" + datestamp + ".log"
log = open(output_directory + logFile, "w")
sys.stdout = log

# Check if to backup dirs exist, if not skip but warn
for item in to_backup:
	if not os.path.exists(item):
		to_backup.remove(item)
		warnings.append("WARNING: {} does not exist so it was skipped.".format(item))

# Check if temp dir exists, if not create it
if temp_directory is not None:
	if not os.path.exists(temp_directory): os.makedirs(temp_directory)

try:
	archive(to_backup,output_directory,temp_directory,nosp_name,datestamp)
	message = "{} completed successfully :D\n{}".format(full_name,datetime_stamp("timestamp"))

except Exception as e: 
	# Capture errors and write to log
	print "ERROR: {}".format(str(e))
	message = "{} FAILED :'(\n{}\n\nHere's the error:\n{}".format(full_name,datetime_stamp("timestamp"),str(e))

finally:
	# If there are warnings, add them to message
	if len(warnings) > 0:
		message += "\n\n"
		for warning in warnings:
			message += warning + "\n"
			print warning

	send_email(message,full_name)

	# Reset sys.stdout and close log file
	sys.stdout = sys.__stdout__
	log.close()