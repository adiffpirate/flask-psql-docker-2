Simple docker-compose project that deploys a Flask app with PostgresQL as its database :)

Components:
  - Docker
  - Docker Compose
  - Flask (Python Framework) (back-end/front-end)
  - PostgresQL with PGAdmin (database)

## Deployment

Requiments:
  - Docker (https://docs.docker.com/engine/install/)
  - Docker Compose (https://docs.docker.com/compose/install/)

Thanks to docker-compose we only need to run one command :)
```sh
docker-compose up --build -d
```

### Access

- Application: http://localhost:8080
- PostgresQL:  localhost:5432

### Dev mode

You can run the project on development mode to enable debug, hot-reloading and deploy a PGAdmin page.

```sh
docker-compose -f docker-compose.yml -f docker-compose.override.dev.yml up --build -d
```

The PGAdmin will be availabe at http://localhost:7777
