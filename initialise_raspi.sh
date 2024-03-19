#!/bin/bash
whoami
date

chmod +x initialise_raspi.sh

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

#installing docker (learn more here: https://raspberrytips.com/docker-on-raspberry-pi/)
if docker --version; then
    echo "Docker already installed"
else
    echo "Installing Docker onto your system"
    curl -sSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "Docker successfully installed"
fi 

#install code
echo "installing python scripts onto your system"
cd /home/$USER/Documents
mkdir vision-system
cd ./vision-system
git clone https://github.com/adbouk-1/4-week-project.git
echo "python scripts successfully installed"

#copy model to code location
# echo "Copying classifier model to the project directory"
# mv "$SCRIPT_DIR/model.h5" /home/$USER/Documents/vision-system/4-week-project/src/classifier/models/
# echo "Copy was successful"

#build data storage directory
mkdir /home/$USER/Documents/data

#build docker container
echo "Building Docker Container"
cd /home/$USER/Documents/vision-system/4-week-project/
docker build -t raspi_script .
echo "Docker Container successfully built"
