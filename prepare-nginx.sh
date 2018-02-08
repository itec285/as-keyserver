   56  # START OF NGINX#
   57  sudo apt-get update
   58  sudo apt-get install python3-pip python3-dev nginx
   60  sudo pip3 install virtualenv
   62  cd ~
   64  mkdir keyserver
   66  cd keyserver
   86  virtualenv myprojectenv
   87  source myprojectenv/bin/activate
   88  pip install uwsgi flask
   90  cp ~/as-keyserver/app.py .
   93  pip install flask-restful
   94  pip install flask-sqlalchemy
   97  sudo cp /home/asadmins/licenseKey.db .
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
