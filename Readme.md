# Secure by design service with FastAPI

this repository create for test security from [mozilla Observatory](https://observatory.mozilla.org)

### score result this service 120/100 


## Build Setup

```bash
# install dependencies
$ pip install -r requirements.txt

# serve with hot reload at localhost:8000
$ cd signature_middleware
$ uvicorn server.main:app --reload --host 0.0.0.0 --port 8080

# build for production and launch docker container
$ docker-compose up -d  # you can access host url http://localhost:8081
$ docker ps # check your containers
```
For detailed explanation on how things work, check out the [documentation](https://fastapi.tiangolo.com).

Base Dependencies:
- JWT
- MongoDB
- Redis

![Alt text](https://github.com/watcharap0n/test-security-observatory-fastapi/blob/main/signature_middleware/server/static/vulner-test.png?raw=true "Title")


