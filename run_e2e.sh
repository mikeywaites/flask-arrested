docker-compose up -d api
docker exec -it flask-arrested_api_1 python example/fixtures.py
sleep 10
docker-compose run --rm e2e_tests
docker-compose stop
