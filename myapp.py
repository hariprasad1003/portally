import dropbox
from werkzeug.utils import secure_filename

dropbox_access_token='sl.A6h_mHgkMYkojZX-kJlN9-2V0FDowb5PUYyIj3hwxM4aXySQAbNufZSrMrVCM_zbfwLG9prMLWbWKyQA_AWGCrGRPmaiH9Xl2waDcNNhtCXBlNTww1BKxJIDfuVB55IT774yGKeRJyM'
computer_path= "app.py"
dropbox_path= "/portally_notes/" + computer_path


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