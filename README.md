# Flatmates 
## The app to manage payments and chores for people living under a roof in a simple and elegant way.

- This repo contains the server side application of the project.
- The client side code is at : https://github.com/VarunSai-DVS/flatmates-client

## Versions
1) python: >=3.12.0
2) fastapi==0.98.0
3) rest of the dependencies can be found in requirements.txt

## Run using pip
`pip install -r requirements.txt`
`uvicorn app:app -reload`

## Run using conda
If you have conda installed then just run the install.sh bash file on mac and linux.
On windows, run the commands in install.sh file one by one in the virtual environment.

## Run using Docker
uncomment this line in config/db.py:
`#host = os.environ["DATABASE_HOST"]`

and change the host in config/db.py in pymysql.connect from local to the host variable you just uncommented

run:
`docker build --no-cache -t flatmates-backend .`
`docker run -p 8000:8000 -it flatmates-backend`
