git rev-parse HEAD > app/tracker/revision.txt
docker build . --rm --no-cache -t tracardi/tracardi-api:0.7.3-dev
docker push tracardi/tracardi-api:0.7.3-dev
