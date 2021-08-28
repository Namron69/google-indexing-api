# Google Indexing API (Read before starting)

Made on Python 3.8.x

1. Go to https://console.cloud.google.com/ -> APIs & Services -> Credentials
2. Click "Create Credentials" -> "Service account" (Role - Owner, no domain app or other personal data needed).
3. Upload your service account json key to the folder with a python program and name it "cred.json".
4. Create "urls.txt" file in the folder with a python program. Put urls to index in it (1 url = 1 line).
5. Start program and follow intructions in console.

Don't forget to instal oauth2client. Enter in cmd:
pip install oauth2client

!!! Only 200 requests per day (Google API Indexing quota)
