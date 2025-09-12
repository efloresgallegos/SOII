# Imagen base
FROM node:20-alpine

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Copiamos sólo el archivo de la aplicación (no copiamos node_modules)
COPY app.js .

# Exponemos el puerto que la aplicación usará
EXPOSE 3000

#Definimos el comando que se ejecutará al iniciar el contenedor
CMD ["node", "app.js"]