# import the required libraries
from __future__ import print_function
import pickle
import os.path
import io
import shutil
import requests

from datetime import date, timedelta, datetime
from mimetypes import MimeTypes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

from os import listdir
from os.path import isfile, join

# path_pc = "/home/jrubio/Documentos/VENVS/SANCOR3/tiffs/"
path_pc = "/mnt/datos/Repositorio/sancor/indices/mndwi/"

path_drive = "_App0_Dwnld"
pais = "_MNDWI_AR."
file_date = date.today() - timedelta(days=5)
#file_date = "2021-05-15"
#file_date = sys.argv[1] #Fecha de procesamiento

#
# Class to manage drive files
#
class DriveAPI:
	global SCOPES

	# Define the scopes
	SCOPES = ['https://www.googleapis.com/auth/drive']

    #
    # Instantiate class
    #
	def __init__(self):

		# Variable self.creds will
		# store the user access token.
		# If no valid token found
		# we will create one.
		self.creds = None

		# The file token.pickle stores the
		# user's access and refresh tokens. It is
		# created automatically when the authorization
		# flow completes for the first time.

		# Check if file token.pickle exists
		if os.path.exists('token.pickle'):

			# Read the token from the file and
			# store it in the variable self.creds
			with open('token.pickle', 'rb') as token:
				self.creds = pickle.load(token)
				print(self.creds)

		# If no valid credentials are available,
		# request the user to log in.
		if not self.creds or not self.creds.valid:

			# If token is expired, it will be refreshed,
			# else, we will request a new one.
			if self.creds and self.creds.expired and self.creds.refresh_token:
				self.creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
					'credentials.json', SCOPES)
				self.creds = flow.run_local_server(port=0)

			# Save the access token in token.pickle
			# file for future usage
			with open('token.pickle', 'wb') as token:
				pickle.dump(self.creds, token)

		# Connect to the API service
		self.service = build('drive', 'v3', credentials=self.creds)

		print(self.service.files())

#		# request a list of first N files or
#		# folders with name and id from the API.
#		results = self.service.files().list(
#			pageSize=200, q="mimeType='image/tiff'", fields="files(id, name)").execute()
#		items = results.get('files', [])

#		# print a list of files

#		print("Here's a list of files: \n")
#		print(*items, sep="\n", end="\n\n")

	#
	# Method to list drive files
	#
	# drive_dir_name:
	# pc_dir_name:
	# file_date:
	#
	def FileList(self,drive_dir_name,file_name):
#		print(file_date)
		# First, get the folder ID by querying by mimeType and name
		folderId = self.service.files().list(q = "mimeType = 'application/vnd.google-apps.folder' and name = '%s'"%drive_dir_name, pageSize=10, fields="nextPageToken, files(id, name)").execute()

		# this gives us a list of all folders with that name
		folderIdResult = folderId.get('files', [])

		# however, we know there is only 1 folder with that name, so we just get the id of the 1st item in the list
		dir_id = folderIdResult[0].get('id')

		# Now, using the folder ID gotten above, we get all the files from
		# that particular folder
		results = self.service.files().list(q = "'%s' in parents and name contains '%s'"%(dir_id,file_name), fields="nextPageToken, files(id, name)").execute()
		items = results.get('files', [])

#		print("Here's a list of files: \n")
#		print(*end_items, sep="\n", end="\n\n")

		return items

    #
    # Method to download files from drive
    #
	def FileDownload(self, file_id, file_name):
		request = self.service.files().get_media(fileId=file_id)
		fh = io.BytesIO()

		# Initialise a downloader object to download the file
		downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
		done = False

		try:
			# Download the data in chunks
			while not done:
				status, done = downloader.next_chunk()

			fh.seek(0)

			# Write the received data to the file
			with open(file_name, 'wb') as f:
				print(file_name)
				shutil.copyfileobj(fh, f)

			print("File Downloaded")
			# Return True if file Downloaded successfully
			return True
		except:

			# Return False if something went wrong
			print("Something went wrong.")
			return False

    #
    # Method to upload files to drive
    #
	def FileUpload(self, filepath):

		# Extract the file name out of the file path
		name = filepath.split('/')[-1]

		# Find the MimeType of the file
		mimetype = MimeTypes().guess_type(name)[0]

		# create file metadata
		file_metadata = {'name': name}

		try:
			media = MediaFileUpload(filepath, mimetype=mimetype)

			# Create a new file in the Drive storage
			file = self.service.files().create(
				body=file_metadata, media_body=media, fields='id').execute()

			print("File Uploaded.")

		except:

			# Raise UploadError if file is not uploaded.
			raise UploadError("Can't Upload File.")


if __name__ == "__main__":
	obj = DriveAPI()

	for yy in range(2021,2022):
		ff = datetime(yy,1,1)
		for dd in range(0,365,8):
			fecha = ff+timedelta(dd)
			fechaj = (ff+timedelta(dd)).strftime("%Y%j")

		file_name = fechaj + pais
		print(file_name)
#	drive_items = obj.FileList(path_drive,path_pc,file_date)
		drive_items = obj.FileList(path_drive,file_name)
		print(len(drive_items))
		print(*drive_items, sep="\n", end="\n\n")
		end_items = drive_items.copy()

	# select pc directory files
		os.chdir(path_pc)
		files_pc = [f for f in listdir(path_pc) if isfile(join(path_pc, f))]

	# Now we can loop through each file in that folder, and do whatever
		for f in range(0, len(drive_items)):
			if drive_items[f].get('name') in files_pc:
				end_items.remove(drive_items[f])
		print(*end_items, sep="\n", end="\n\n")

		list_id = []
		list_name = []
		for f in range(len(end_items)):
			list_id.append(end_items[f].get('id'))
			list_name.append(end_items[f].get('name'))

		resultado = list(map(obj.FileDownload,list_id,list_name))

#	for f in range(0, len(end_items)):
#		print(f)
#		f_id = end_items[f].get('id')
#		f_name = end_items[f].get('name')
#		obj.FileDownload(f_id, f_name)

#	i = int(input("Enter your choice: 1 - Download file, 2- Upload File, 3- Exit.\n"))
#
#	if i == 1:
#		f_id = input("Enter file id: ")
#		f_name = input("Enter file name: ")
#		obj.FileDownload(f_id, f_name)
#
#	elif i == 2:
#		f_path = input("Enter full file path: ")
#		obj.FileUpload(f_path)
#
#	else:
#		exit()
