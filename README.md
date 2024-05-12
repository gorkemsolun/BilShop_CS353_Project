# Setup

Install and open Docker

Move your current operating system's yaml file from yaml/\<Operating System\> to the project's folder.

Open the terminal in the project's folder.

Enter `docker build -t app .` to create an image tagged app, this needs to be the case since yaml configuration configures the image named app.

Then, enter the `docker-compose build` command to build a container.

Lastly `docker-compose up` command will be used to dynamically run and connect database and web configuration of the container.
Alternatively you can use `docker-compose up .` to statically connect the database and web configuration created by docker.

Containers can be removed with `docker-compose rm`; if you want to inject insertions through a SQL file, you need to first delete the container and follow the `docker-compose build` and `docker-compose up` commands consecutively.
