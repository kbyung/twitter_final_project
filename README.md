# flask-on-docker

A containerized web-app built using the Instagram tech stack: postgresql database, gunicorn+Flask webserver, and nginx for load balancer. This repo contains a production-ready Docker Compose file to handle the uploading of static and media files. 

## Upload Functionality

The GIF below showcases the upload functionality of the web-app. 

## Build Instructions

**Development**
Start the development environment
`$ docker compose up -d --build`

Initialize the database
`$ docker compose exec web manage.py create_db`

Access the database
`$ docker compose exec db psql --username=hello_flask --dbname=hello_flask_dev`

**Production**
Start the production environment
`$ docker compose -f docker-compose.prod.yml up -d --build` 

Initialize the database
`$ docker compose -f docker-compose.prod.yml exec web python manage.py create_db`

Access the database
`$ docker compose exec db psql --username=hello_flask --dbname=hello_flask_prod`

