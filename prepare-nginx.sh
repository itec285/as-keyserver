# START OF NGINX#  see https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04

sudo apt-get update
sudo apt-get install python3-pip python3-dev nginx
sudo pip3 install virtualenv
cd ~
mkdir keyserver
cd keyserver
virtualenv myprojectenv
source myprojectenv/bin/activate
pip install uwsgi flask
pip install flask-restful
pip install flask-sqlalchemy
cp ~/as-keyserver/app.py .
cp ~/as-keyserver/licenseKey.db .
cp ~/as-keyserver/addons/wsgi.py .
cp ~/as-keyserver/addons/keyserver.ini .


###TEST with Python###
   98  python app.py 
##Create a new file called wsgi in the current directory.  Populate as follows##
from app import app

if __name__ == "__main__":
	app.run()
###############

##Now, test uwsgi##
uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app

##If it still works, we are done with test environment#
deactivate

###create a file called keyserver.ini, with these contents ###
[uwsgi]
module = wsgi:app

master = true
processes = 5

socket = myproject.sock
chmod-socket = 660
vacuum = true

die-on-term = true
###########################

sudo cp addons/myproject.service /etc/systemd/system/
sudo systemctl start myproject
sudo systemctl enable myproject
sudo cp addons/keyserver /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/keyserver /etc/nginx/sites-enabled/
