# Iconic-Quotes
Iconic dialogues from popular movies and shows. 

### Database Setup
Create a .env file in the root directory with the following content:
```
# .env
DATABASE_URL=mysql+pymysql://user:password@db/quotes_db
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=quotes_db
MYSQL_USER=admin
MYSQL_PASSWORD=admin
```
### Docker Setup
The docker-compose.yml file defines the two services needed for the application to run: the web service (your Flask app) and the db service (the MySQL database).
To run the application, you can use Docker. Make sure you have Docker installed and then run the following commands:
```bash
docker-compose up -d
```
This will start the MySQL database and the Flask application in detached mode.


#### Find out the dependencies and their version numbers
Add ipython to the list of dependencies in `flake.nix` and then run the following command to check the version of Flask:
```bash
import flask
```
```bash
flask.__path__
```
```bash
l flask.__path__ # This will show the symlink path to the flask module with version number
```
