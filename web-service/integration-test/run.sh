#!/usr/bin/env bash

cd "$(dirname "$0")"


LOCAL_IMAGE_NAME="credit-card-attrition":latest

docker build -t ${LOCAL_IMAGE_NAME} ..

export LOCAL_IMAGE_NAME="credit-card-attrition":latest

docker-compose up -d

# docker run -it --rm \
#     -p 8001:8001 \
#     -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
#     -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
#     -e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
#     ${LOCAL_IMAGE_NAME}

sleep 5


pipenv run python test_docker.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi

sleep 1

docker-compose down