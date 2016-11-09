from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import datetime


# User variables
output_dir  = "docs/files/"
credentials = "docs/credentials.json"

gauth = GoogleAuth()

# Try to load saved client credentials
gauth.LoadCredentialsFile(credentials)
if gauth.credentials is None: gauth.LocalWebserverAuth()  # Authenticate if they're not there
elif gauth.access_token_expired: gauth.Refresh()          # Refresh them if expired
else: gauth.Authorize()                                   # Initialize the saved creds

# Save the current credentials to a file
gauth.SaveCredentialsFile(credentials)

drive = GoogleDrive(gauth)

# Create datestamp
t = datetime.datetime.now()
datestamp = "{}-{:02}-{:02}".format(t.year,t.month,t.day)

# Download digitization instructions
file = drive.CreateFile({'id': '1cikDBc4Tf2LgffEZZWNJY4Ea83LdjiFegAgOiDpiDKA'})
file.GetContentFile("{}{}_{}.pdf".format(output_dir,datestamp,file['title']),mimetype='application/pdf')

# Download spreadsheet
file = drive.CreateFile({'id': '1U0i_0zEeJ4eBv5I7YhvHPul0xZZG3pg0VXq57VzPq1M'})
file.GetContentFile("{}{}_{}.xlsx".format(output_dir,datestamp,file['title']),mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')