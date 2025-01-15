

## docker 

docker build --rm -t hackdb-embedding:latest .

docker run --env-file .env --rm  -p 8080:8080 --name hackdb-embedding hackdb-embedding:latest 

docker buildx build -f Dockerfile --platform linux/amd64 --push -t registry.digitalocean.com/smartan/hackdb-embedding:latest .

docker buildx build --platform linux/amd64 --push -t registry.digitalocean.com/smartan/hackdb-embedding:latest .