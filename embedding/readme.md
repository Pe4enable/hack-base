

## docker 

docker build --rm -t hackdb-embedding:latest .

docker run --env-file .env --rm  -p 8000:8000 --name hackdb-embedding hackdb-embedding:latest 