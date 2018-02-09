#!/bin/bash

# This script is designed to prepare a (Ubuntu 16.04.3 at the time of this writing) system for a AS keyserver
#  see https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04 for further details
# Feb 2018 IL

sudo apt-get update
sudo apt install -y python3-pip python3-dev nginx boxes
sudo pip3 install virtualenv
cd ~
mkdir keyserver
cd keyserver
virtualenv myprojectenv

#Prepare the virtual environment
source myprojectenv/bin/activate
pip install uwsgi flask
pip install flask-restful
pip install flask-sqlalchemy

cp ~/as-keyserver/app.py .
cp ~/as-keyserver/licenseKey.db .
cp ~/as-keyserver/addons/wsgi.py .
cp ~/as-keyserver/addons/keyserver.ini .

echo -e "\n\tFirst test, manually with python\n\t" | boxes -d stone
read -rsp $'Press any key to continue...\n' -n 1 key
python app.py 

##Now, test uwsgi##
echo -e "\n\tSecond test, manually with uwsgi\n\t" | boxes -d stone
read -rsp $'Press any key to continue...\n' -n 1 key
uwsgi --socket 0.0.0.0:5000 --protocol=http -w wsgi:app

##If everything works to this point, we are done with test environment#
deactivate

#Create our service
sudo cp addons/myproject.service /etc/systemd/system/
sudo systemctl start myproject
sudo systemctl enable myproject

#Note - keyserver file contains the server address so if it changes you need to update this file
cd ~/as-keyserver
sudo cp addons/keyserver /etc/nginx/sites-available/

sudo ln -s /etc/nginx/sites-available/keyserver /etc/nginx/sites-enabled/

echo -e "Check nginx for errors " | boxes -d stone
sudo nginx -t

sudo systemctl restart nginx

#Allow NGINX traffic through the firewall.
sudo ufw allow 'Nginx Full'

echo -e "\n\tYOU ARE DONE :-)\n\tivanl@auto-star.com\n\twww.auto-star.com" | boxes -d dog
