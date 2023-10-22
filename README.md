# Cloud Conversion Tool
A continuación, encontrarás información sobre la aplicación, cómo configurarla y ejecutarla, así como detalles sobre los servicios REST, la arquitectura y la documentación.

## Tabla de Contenidos

1. [Colaboladores](#colaboladores)
2. [Descripción](#descripción)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Requisitos de Instalación](#requisitos-de-instalación)
5. [Arquitectura](#arquitectura)
6. [API REST](#api-rest)

## Colaboladores
| Nombre y apellidos | Correo|
| --- | --- |
| Camilo Ramírez Restrepo​ | c.ramirezr2@uniandes.edu.co |
| Laura Daniela Molina Villar​ | ld.molina11@uniandes.edu.co |
| Leidy Viviana Osorio Jiménez​ | l.osorioj@uniandes.edu.co |
| Tim Ulf Pambor | l.osorioj@uniandes.edu.co |
| Shadith Perez Rivera | s.perezr@uniandes.edu.co |

## Descripción
Aplicación web que ofrece gratuitamente a usuarios de internet, puedan subir abiertamente diferentes formatos multimedia de archivos y cambiarles su formato o realizar procesos de compresión. El modelo general de funcionamiento de la aplicación se basa en crear una cuenta en el portal web y acceder al administrador de archivos. Una vez la cuenta ha sido creada, el usuario puede subir archivos y solicitar el cambio de formato de estos para descargarlos. La aplicación web le permite a un usuario convertir archivos multimedia en línea de un formato a otro, seleccionando únicamente el formato destino. La aplicación se enfoca en la conversión de formatos de video, incluyendo MP4, WEBM, AVI, MPEG y WMV.

## Tecnologías Utilizadas

- Python
- Flask
- Docker

## Requisitos de Instalación

1. Clona este repositorio.
2. Instala las dependencias utilizando el gestor de paquetes de Python:
   ```bash
   pip install -r requirements.txt

## Arquitectura 
- Vista de Contexto y dominio​
- Vista Información​
- Vista Funcional
- Vista de Despliegue

[Video Presentacion](https://uniandes-my.sharepoint.com/:v:/g/personal/ld_molina11_uniandes_edu_co/EZXky1x7CAxBsCGKHg3t-jQBG-ErSnNLD5Bermb0M9LMTA?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZyIsInJlZmVycmFsQXBwUGxhdGZvcm0iOiJXZWIiLCJyZWZlcnJhbE1vZGUiOiJ2aWV3In19&e=jD1bpe)

Consulta la documentación completa de la arquitectura. 
- [Documento](Docs)
- [Video](https://uniandes-my.sharepoint.com/:v:/g/personal/ld_molina11_uniandes_edu_co/EQVFU8pj7rtPpH6xZ7xeNDwBo4eb3ASiZOXjZMw0Bhz1rw?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZyIsInJlZmVycmFsQXBwUGxhdGZvcm0iOiJXZWIiLCJyZWZlcnJhbE1vZGUiOiJ2aWV3In19&e=k4icLV)

## API REST
- /api/crear-cuenta (POST): Crea una cuenta de usuario.
- /api/iniciar-sesion (POST): Inicia sesión en la aplicación web.
- /api/listar-tareas (GET): Lista todas las tareas de conversión de un usuario.
- /api/subir-archivo (POST): Sube y cambia el formato de un archivo.
- /api/info-tarea/{id} (GET): Obtiene información de una tarea de conversión específica.
- /api/borrar-archivo/{id} (DELETE): Borra el archivo original y el archivo convertido de un usuario

[Postman Collection](https://github.com/tpambor/MISW4204/blob/main/Cloud%20Conversion%20Tool.postman_collection.json)

Consulta la documentación completa de la API aqui: 
- [Documentacion en Postman](https://documenter.getpostman.com/view/29422849/2s9YRB4CyY) 
- [Escenario y Pruebas de Estrés API REST y Batch](https://github.com/tpambor/MISW4204/blob/main/Docs/Escenario%20y%20Pruebas%20de%20Estr%C3%A9s%20API%20REST%20y%20Batch.docx)
- [Video](https://uniandes-my.sharepoint.com/:v:/g/personal/ld_molina11_uniandes_edu_co/EUsm0jWJLKJHigp_zkCJOAwB0MCSva_fnDBUKZSaOIyIiA?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZyIsInJlZmVycmFsQXBwUGxhdGZvcm0iOiJXZWIiLCJyZWZlcnJhbE1vZGUiOiJ2aWV3In19&e=q7VTWj)

## Escenario y Pruebas de Estrés API REST y Batch 
El objetivo de este plan es evaluar la capacidad de la aplicación de convertidor de archivos y su infraestructura de soporte en un entorno tradicional para determinar sus máximos aceptables. El objetivo es comprender cómo la aplicación responde a diferentes niveles de carga de usuarios y cuál es su capacidad máxima. 

- [Documento Escenario y Pruebas de Estrés API REST y Batch](Docs)
- [Video Pruebasde Estrés](https://uniandes-my.sharepoint.com/:v:/g/personal/ld_molina11_uniandes_edu_co/EUVAVJJbgaNHlVBGZy_jVaEBy4zqGt0Df2BDPBx0hSXO3Q?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0RpcmVjdCJ9fQ&e=yV8giC)
