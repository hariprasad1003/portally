import dropbox
from werkzeug.utils import secure_filename



client = dropbox.Dropbox(dropbox_access_token)


# client.files_upload(computer_path,dropbox_path)

with open(computer_path, 'rb') as f:
            client.files_upload(f.read(), dropbox_path)
            print("uploaded")

md, res = client.files_download(dropbox_path)
data = res.content

f = open(computer_path, "wb")
f.write(data)
f.close()