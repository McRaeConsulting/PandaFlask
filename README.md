# A Flask of Pandas

Example project that uses python (flask) as web app to display ONS deaths data using Google charts. Using pandas to read data from the ONS published excel spreadsheet and transform said data into a format usable by Google charts.

Includes a docker-compose file to containerise it. The docker is using traefik, nginx and gunicorn to turn it into a web app.
