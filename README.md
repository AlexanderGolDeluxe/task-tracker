# Project task-tracker
REST API for tracking and managing team tasks with user registration and role-based authorization.  
Developed on the [FastAPI](https://fastapi.tiangolo.com) framework.  
Test task for [The Originals](https://theoriginals.com.ua)

![Static Badge](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=blue&labelColor=white)
![Static Badge](https://img.shields.io/badge/FastAPI-0.115.0-009485?logo=fastapi&labelColor=white)
![Static Badge](https://img.shields.io/badge/PostgreSQL-white?logo=postgresql)

## Installation

### Clone repository
```console
git clone https://github.com/AlexanderGolDeluxe/task-tracker
```

### Make a virtual environment with requirements

```console
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Generate RSA private key + public key pair

Create a directory to store certificates
```console
mkdir ./certs
```

Generate an RSA private key, of size 2048
```shell
openssl genrsa -out certs/jwt-private.pem 2048
```

Extract the public key from the key pair, which can be used in a certificate
```shell
openssl rsa -in certs/jwt-private.pem -outform PEM -pubout -out certs/jwt-public.pem
```

### Manage environment variables

Rename file [`.env.dist`](/.env.dist) to `.env`
```console
mv .env.dist .env
```

#### Change variables according to your required parameters in `.env` file

Enter the configuration data of SMTP server to perform mail notification.  
Tested using the [Ethereal](https://ethereal.email) service
```
…
### MAIL SETTINGS ###
MAIL_HOST = "smtp.email"
MAIL_USERNAME = "example@smtp.email"
MAIL_PASSWORD = "******************"
MAIL_PORT = 587
…
```

Set your PostgreSQL database variables
```
…
### POSTGRESQL SETTINGS ###
PG_USER = "postgres"
PG_PASSWORD = "********"
PG_HOST = "localhost"
PG_PORT = 5432
…
```

> <span style="color:yellow">***WARNING***</span>  
*If you don't want to use PostgreSQL database, just leave* `PG_DB_URL` *variable empty. SQLite3 will be used instead*
```
…
PG_DB_URL = ""
…
```

## Launch

```console
uvicorn app:create_app --reload
```

## Build via Docker compose

1. [Clone repository](#clone-repository)
2. [Rename file `.env.dist` to `.env`](#manage-environment-variables)
3. [Change variables according to your required parameters in `.env` file](#change-variables-according-to-your-required-parameters-in-env-file)
4.  Run following command in your console:
    ```console
    docker compose -f "docker-compose.yml" up -d --build
    ```
