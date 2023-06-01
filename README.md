# recipe-api

Recipe API based on Django REST Framework, Docker, PostgreSQL, Nginx, Uwsgi.

## ToDo

- JWT replacement for Django Auth Token
- Instead docker-compose; swarm or kubernetes deploy files

## To use in production

### AWS Ubuntu Setup

- Install docker requirements and add **ubuntu** user to **docker** group, needs reboot system.

```shell
sudo apt install docker-compose docker.io docker
sudo usermod -aG docker ubuntu
```

- Clone repository: `git clone https://github.com/cihatertem/recipe-api.git`

- Create environment inside copied project folder:

```shell
cd recipe-api/
mkdir environment
cp variables_sample.txt environment/variables_prod.txt
```

- Change variables-prod.txt keys with your own credentials & variables.

- Start the project: `docker-compose -f docker-compose-prod.yaml up --build -d`

- Create a superuser for API admin: `docker-compose -f docker-compose-prod.yaml run --rm app-prod sh -c "python manage.py createsuperuser"`

- If you need to stop API: `docker-compose -f docker-compose-prod.yaml down --remove-orphans`

- If you need stop API and remove volumes (You're going to lose every data, database too): `docker-compose -f docker-compose-prod.yaml down --remove-orphans -v`

- Updating APP(inside project folder **recipe-api**):

```shell
docker-compose -f docker-compose-prod.yaml down --remove-orphans
git pull origin
docker-compose -f docker-compose-prod.yaml up --build -d
```

- View logs: `docker-compose -f docker-compose-prod.yml logs`