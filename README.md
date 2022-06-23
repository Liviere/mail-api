# Mail-API

An simple API application to handle sending mails from the frontend services.
It's mainly based on [FastAPI](https://fastapi.tiangolo.com/).

It has built-in request validations. It also protects against too frequent sending of e-mails.

## Configuration

First, before begin, set the application config with the `settings.py` file.

### Example:

```python
from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Predefined solutions for the production stage
    PRODUCTION = False

    # Email Server Hostname
    MAIL_HOST = "iredmail"

    # CORS
    ORIGINS: List[str] = [
        "https://domain1.com",
        "https://domain2.pl",

    # Services Name
    SERVICES = ["service-name-1", "service-name-2"]

    # Services Domains
    DOMAINS = {
        SERVICES[0]: "domain1.com",
        SERVICES[1]: "domain2.pl"
    }

    # Services keys to authentication
    SERVICES_KEYS = {
        SERVICES[0]: "SECRET_KEY_1",
        SERVICES[1]: "SECRET_KEY_2"
    }

    # Mail users credentials required to connect by SMTP
    MAIL_USERS = {
        SERVICES[0]: ("user@domain1.com", "USER1_PASSWORD"),
        SERVICES[1]: ("user@domain2.pl", "USER1_PASSWORD")
    }

    # Default mails to receive the messages
    MAIL_TO = {
        SERVICES[0]: "contact@domain1.com",
        SERVICES[1]: "contact@domain2.pl"
    }

    REDIS_CRE = {
        "host": "mail-redis",
        "port": 6379
    }

    # Redis cache names
    REQUESTS_IP_CACHE = "default"
    REQUESTS_SID_CACHE = "requests-sid"
    REQUESTS_COMPLEX_CACHE = "complex-cache"

    # Token Settings
    ALGORITHM = "SHA256"  # e.g SHA256 | HS256 | HS384
    TOKEN_HASH = "SECRET_KEY"
    ACCESS_TOKEN_NAME = "accessToken"
    ACCESS_COOKIE_NAME = "access-token"
    ACCESS_TOKEN_EXPIRE_TIME = 3600
    ACCESS_COOKIE_EXPIRE_TIME = 3600

    # Documentation url
    DOCS_URL = False  # e.g "/docs" | False
```

## Usage

To send a message, you have to send a POST request to route `/api/v1/send` with formData which contains:

- recipients: List[str] `required`,
- subject: str `required`,
- html: str,
- plaintext: str,
- files: List[UploadFile]),

It must also have an Bearer authorization header with access token.
You can get it by sending a POST request to `/api/v1/token` with service name and password.

> :warning: it's best to do it on the server side, and then pass the token to the client. Otherwise, someone might use your access without you knowing.

### Javascript Examples:

```javascript
## Getting the access token

const formDataAsString = `username=${SERVICE_NAME}` + `&password=${SERVICE_PASSWORD}`;
await axios({
	method: 'POST',
	data: formDataAsString,
	headers: {
		Authorization: `Bearer ${accessToken}`,
	},
	url: `${API_HOSTNAME}/api/v1/token`,
})

## Sending a message

await axios({
	method: 'POST',
	data: formData,
	headers: {
		Authorization: `Bearer ${accessToken}`,
	},
	url: `${API_HOSTNAME}/api/v1/send`,
})
```

## Deployment

### Docker

1. Clone the repository.

2. Set your own docker configuration with docker-compose.yml (Optional).

3. Build and run docker containers.

```bash
docker-compose up
```

## Update

Pull the latest version from the git.

```bash
git fetch
git pull
```

### Only mail-api container

```bash
docker stop mail-api
docker rm mail-api
docker image rm mail-api:latest
docker-compose up -d mail-api
```

### Both containers

```bash
docker-compose up --force-recreate --build -d
docker image prune -f
```

## Development

1. Set the python enviroment.

> :warning: The application require at least Python 3.8 or newer.

```bash
# Create and acivate Virtual Environment
python3.8 -m venv venv
source venv/bin/activate

# Upgade pip and install modules
cd ./app
pip install --upgrade pip
pip install -r requirements.txt
```

2. Run the application

```bash
uvicorn main:app --reload
```
