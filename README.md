# Cloud Conversion Tool

Una aplicación web que permite a los usuarios convertir diferentes formatos multimedia de archivos y realizar procesos de conversion de forma gratuita.
Pueden  tener la administración de los archivos y tener una sección de registro y login, al mismo tiempo que se asegura la autenticación y control de acceso de los usuarios.

## Tabla de Contenidos

1. [Colaboladores](#colaboladores)
2. [Descripción](#descripción)
3. [Características](#características)
4. [Tecnologías Utilizadas](#tecnologías-utilizadas)
5. [Requisitos de Instalación](#requisitos-de-instalación)
6. [API REST](#api-rest)
7. [Despliegue](#despliegue)

## Colaboladores
- Camilo Ramírez Restrepo​
- Laura Daniela Molina Villar​
- Leidy Viviana Osorio Jiménez​
- Tim Ulf Pambor ​
- Shadith Perez Rivera

## Descripción

Una nueva compañía de cloud denominada Cloud Conversion Tool desea crear una aplicación web que permita a los usuarios subir diferentes formatos multimedia de archivos y cambiarles su formato o realizar procesos de compresión. Los usuarios deben crear una cuenta para acceder a las funciones de conversión y compresión de archivos.

## Características
- Conversión entre formatos de video: MP4, WEBM, AVI, MPEG, WMV.

## Tecnologías Utilizadas

- Python
- Flask
- Docker

## Requisitos de Instalación

1. Clona este repositorio.
2. Instala las dependencias utilizando el gestor de paquetes de Python:
   ```bash
   pip install -r requirements.txt

## API REST
- /api/crear-cuenta (POST): Crea una cuenta de usuario.
- /api/iniciar-sesion (POST): Inicia sesión en la aplicación web.
- /api/listar-tareas (GET): Lista todas las tareas de conversión de un usuario.
- /api/subir-archivo (POST): Sube y cambia el formato de un archivo.
- /api/info-tarea/{id} (GET): Obtiene información de una tarea de conversión específica.
- /api/borrar-archivo/{id} (DELETE): Borra el archivo original y el archivo convertido de un usuario

Consulta la documentación completa de la API aqui: https://documenter.getpostman.com/view/29422849/2s9YRB4CyY 
