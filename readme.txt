APPLICATION:
========
vm_manager 


DESCRIPTION:
============
An Application that is used to create/ checkout/ checkin/ delete Virtual Machines. This application uses a mysql data base to store the information related to the Virtual Machines. The user can use the RESTFul API built using Flask framework to checkin/ checkout the Virtual Machines


FILE LIST: 
==========
Dockerfile			Docker file containing the steps to build the Docker image
docker-compose.yml		File that contains information about how the db container and the 
				 application container are to be run
init.sql			File that contains the information to initialize the MYSQL DataBase
requirements.txt		list of required packages to be installed 
app.py				Flask app
virtualMachineAdmin.py		Contains the VirtualMachineAdmin Class that has the VM related methods 
tests.py			Unit tests for the VirtualMachineAdmin Class



REQUIREMENTS:
=============
The application is developed in Python3.6. It requires the Flask and mysql-connector libraries. 


LIBRARIES:
=========
Following is the list of the libraries that have been used in developing the Application and writing the unit tests: 
json		threading 		uuid		random		
time 		mysql.connector		flask		sqlite3	
unittest	concurrent.futures


INSTALLATION: 
=============
1. Download / clone the code from the GitHub repo found at https://github.com/sushwanth/vm_manager 
2. cd into the directory having the DockerFile. 
3. If you do not have Docker installed in your linux box, you can install it by using the install.sh script found here: https://github.com/docker/docker-install
4. Use the command -> "$ docker-compose build " to build a docker image. This command would build a docker image by using the information given in the Dockerfile 
5. Use the command -> "$ docker-compose up" to start app. This would start the mysql container first followed by the application container as specified in the docker-compose.yml file 
6. Now, you can check if the server is running by visiting the url "http://127.0.0.1:5000/" (Alternatively, you can use the curl command as well)


EXAMPLES: 
=========

CreateVM: 

Command 	:  curl  "http://127.0.0.1:5000/createVM/"
Response 	:  "{\"status\": \"success\", \"data\": {\"vm_id\": \"1dc39711-198a-4b7a-9cf9-1c937a7f55f5\", \"ip\":\"212.23.243.201\", \"vm_status\": \"error\"}, \"message\": null}"

CheckoutVM: 

Command		:  curl  "http://127.0.0.1:5000/checkoutVM/"
Response	:  "{\"status\": \"success\", \"data\": {\"vm_id\": \"de819506-6e2e-4168-93aa-b43a73bd0985\", \"ip\": \"39.36.199.250\", \"vm_status\": \"checked-out\"}, \"message\": null}"


CheckinVM: 

Command		:  curl "http://127.0.0.1:5000/checkinVM/?unique_id=de819506-6e2e-4168-93aa-b43a73bd0985&ip=39.36.199.250"
Response	:  "{\"status\": \"success\", \"data\": {\"vm_id\": \"de819506-6e2e-4168-93aa-b43a73bd0985\", \"ip\": \"39.36.199.250\", \"vm_status\": \"available\"}, \"message\": null}"

GetVM: 

Command		:  curl "http://127.0.0.1:5000/getVM/?unique_id=de819506-6e2e-4168-93aa-b43a73bd0985&ip"
Response	:  "{\"status\": \"success\", \"data\": {\"vm_id\": \"de819506-6e2e-4168-93aa-b43a73bd0985\", \"ip\": \"39.36.199.250\", \"vm_status\": \"available\"}, \"message\": null}"

GetVMStatus: 

Command		: curl "http://127.0.0.1:5000/getVMStatus/?unique_id=de819506-6e2e-4168-93aa-b43a73bd0985&ip"
Response	: "{\"status\": \"success\", \"data\": {\"vm_status\": \"available\"}, \"message\": null}"


TESTS: 
======
The unit tests have been written in the file: tests.py 
You can run the unit tests for the VirtualMachineAdmin class methods by running the tests.py file 

To run the unit tests use the command -> "$ python tests.py " (please make sure you are using python3)


