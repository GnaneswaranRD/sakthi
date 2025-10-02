FROM python:3.13-bullseye

ENV IS_DOCKER_BUILD="1"
ENV HOME="/root"
ENV PROJECT_DIR="/app"

WORKDIR ${PROJECT_DIR}

# not copying the source code, when needed directly mounting the files.
COPY . .

# install requiered packages and setuptools
RUN pip install -r requirements.txt && pip install -U setuptools


CMD ["python manage.py runserver"]