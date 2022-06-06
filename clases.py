import os
import pickle
import io

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

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

		# The file token.pickle stores thedriveDownload
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

		print(file_name)
		try:
			# Download the data in chunks
			while not done:
				status, done = downloader.next_chunk()
			fh.seek(0)

			# Write the received data to the file
			with open(file_name, 'wb') as f:
				shutil.copyfileobj(fh, f)

			print("File Downloaded")
			# Return True if file Downloaded successfully
			return file_name

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
