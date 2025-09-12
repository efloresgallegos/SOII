Descargar MARIADB y wordpress

docker pull mariadb:10.11
docker pull wordpress

docker run -d \
  --name wp-db \
  -e MYSQL_ROOT_PASSWORD=MiClaveSecreta \
  -e MYSQL_DATABASE=wordpress \
  -e MYSQL_USER=wp_user \
  -e MYSQL_PASSWORD=MiClaveSecreta \
  mariadb:10.11

  docker run -d \
  --name wp \
  --link wp-db:mysql \
  -e WORDPRESS_DB_HOST=wp-db:3306 \
  -e WORDPRESS_DB_USER=wp_user \
  -e WORDPRESS_DB_PASSWORD=MiClaveSecreta \
  -e WORDPRESS_DB_NAME=wordpress \
  -p 8080:80 \
  wordpress:latest

  docker run -d \
  --name wp \
  --link wp-db:mysql \
  -e WORDPRESS_DB_HOST=wp-db:3306 \
  -e WORDPRESS_DB_USER=wp_user \
  -e WORDPRESS_DB_PASSWORD=MiClaveSecreta \
  -e WORDPRESS_DB_NAME=wordpress \
  -p 8080:80 \
  wordpress:latest