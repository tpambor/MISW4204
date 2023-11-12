# Cloud Conversion Tool
A continuación, encontrarás información sobre la aplicación, cómo configurarla y ejecutarla, así como detalles sobre los servicios REST, la arquitectura y la documentación.

## Tabla de Contenidos

1. [Integrantes](#integrantes)
2. [Descripción](#descripción)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Requisitos de Instalación](#requisitos-de-instalación)
5. [Arquitectura](#arquitectura)
6. [API REST](#api-rest)

## Integrantes
| Nombre y apellidos | Correo|
| --- | --- |
| Camilo Ramírez Restrepo​ | c.ramirezr2@uniandes.edu.co |
| Laura Daniela Molina Villar​ | ld.molina11@uniandes.edu.co |
| Leidy Viviana Osorio Jiménez​ | l.osorioj@uniandes.edu.co |
| Tim Ulf Pambor | t.pambor@uniandes.edu.co |
| Shadith Perez Rivera | s.perezr@uniandes.edu.co |

## Sustentación
[Video Entrega 3](https://uniandes-my.sharepoint.com/:v:/g/personal/ld_molina11_uniandes_edu_co/EVBmocJw6JVMtB-i-m353gEBtQ2Jya8inYP6IFat20XnVA?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0RpcmVjdCJ9fQ&e=RbEcdP)

[Video Entrega 2](https://uniandes-my.sharepoint.com/:v:/g/personal/ld_molina11_uniandes_edu_co/ESXecRTbUxpKisAP5cWweW4B4SUSKG880KrYFCgVAyrz6w?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0RpcmVjdCJ9fQ&e=3UmHj0)

[Video Entrega 1](https://uniandes-my.sharepoint.com/:v:/g/personal/ld_molina11_uniandes_edu_co/EVyhEdkcFvdHuasJB6z8HK8B3smzySw0qnnNRPWPndmBHg?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0RpcmVjdCJ9fQ&e=8ZVKQh)

## Descripción
Aplicación web que ofrece gratuitamente a usuarios de internet, puedan subir abiertamente diferentes formatos multimedia de archivos y cambiarles su formato o realizar procesos de compresión. El modelo general de funcionamiento de la aplicación se basa en crear una cuenta en el portal web y acceder al administrador de archivos. Una vez la cuenta ha sido creada, el usuario puede subir archivos y solicitar el cambio de formato de estos para descargarlos. La aplicación web le permite a un usuario convertir archivos multimedia en línea de un formato a otro, seleccionando únicamente el formato destino. La aplicación se enfoca en la conversión de formatos de video, incluyendo MP4, WEBM, AVI, MPEG y WMV.

## Tecnologías Utilizadas

- Docker + Docker Compose
- Python3
- Flask
- Celery
- Redis
- PostgreSQL
- SQLAlchemy
- nginx
- gunicorn

## Requisitos de Instalación

1. Instalar Docker y Docker Compose
2. Clona este repositorio.
3. Ejecuta `docker compose build` para crear los diferentes contenedores
4. Ejecuta `docker compose up` para ejecutar la aplicación

## Arquitectura 
- Vista de Contexto y dominio​
- Vista Información​
- Vista Funcional
- Vista de Despliegue

Consulta la documentación completa de la arquitectura. 
- [Entrega 1 - Arquitectura tradicional](https://github.com/tpambor/MISW4204/blob/main/Docs/Entrega%201%20-%20Arquitectura%2C%20conclusiones%20y%20consideraciones.pdf)
- [Entrega 2 - Arquitectura Cloud](https://github.com/tpambor/MISW4204/blob/main/Docs/Entrega%202%20-%20Arquitectura%2C%20conclusiones%20y%20consideraciones.pdf)
- [Entrega 3 - Arquitectura Cloud con escalabilidad en la capa web](https://github.com/tpambor/MISW4204/blob/main/Docs/Entrega%203%20-%20Arquitectura%2C%20conclusiones%20y%20consideraciones.pdf)
    
## API REST
- /api/auth/signup (POST): Crea una cuenta de usuario.
- /api/auth/login (POST): Inicia sesión en la aplicación web.
- /api/tasks (GET): Lista todas las tareas de conversión de un usuario.
- /api/tasks (POST): Sube y cambia el formato de un archivo.
- /api/tasks/{{task_id}} (GET): Obtiene información de una tarea de conversión específica.
- /api/tasks/{{task_id}} (DELETE): Borra el archivo original y el archivo convertido de un usuario

Consulta la documentación completa de la API aqui: 
- [Documentacion en Postman](https://documenter.getpostman.com/view/29422849/2s9YRB4CyY) 
- [Postman Collection](https://github.com/tpambor/MISW4204/blob/main/Cloud%20Conversion%20Tool.postman_collection.json)

## Escenario y Pruebas de Estrés API REST y Batch 
El objetivo de este plan es evaluar la capacidad de la aplicación de convertidor de archivos y su infraestructura de soporte en un entorno tradicional para determinar sus máximos aceptables. El objetivo es comprender cómo la aplicación responde a diferentes niveles de carga de usuarios y cuál es su capacidad máxima. 

- [Documento Escenario y Pruebas de Estrés API REST y Batch](https://github.com/tpambor/MISW4204/blob/main/Docs/Escenario%20y%20Pruebas%20de%20Estr%C3%A9s%20API%20REST%20y%20Batch.pdf)

## Configuración Escenario 1 JMeter
- [Configuración](https://github.com/tpambor/MISW4204/blob/main/Docs/Experimento%201%20-%20Configuraci%C3%B3n.pdf)
- [Video](https://uniandes-my.sharepoint.com/personal/ld_molina11_uniandes_edu_co/_layouts/15/stream.aspx?id=%2Fpersonal%2Fld%5Fmolina11%5Funiandes%5Fedu%5Fco%2FDocuments%2FDesarrollo%20de%20software%20en%20la%20nube%2FSemana%203%2FVideo%2F2%2E%20Experimento%201%2Emp4&referrer=StreamWebApp%2EWeb&referrerScenario=AddressBarCopied%2Eview)

## Configuración Escenario 2 Script GCP
- [Configuración](https://github.com/tpambor/MISW4204/blob/main/Docs/Experimento%202%20-%20Configuraci%C3%B3n.pdf)
- [Video](https://uniandes-my.sharepoint.com/:v:/g/personal/ld_molina11_uniandes_edu_co/ERowgNb9SNxNhRiheiM35FgB8seEdbRzYU2Gky1t6o4FHQ?e=CIxKvy&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZyIsInJlZmVycmFsQXBwUGxhdGZvcm0iOiJXZWIiLCJyZWZlcnJhbE1vZGUiOiJ2aWV3In19)
