# Builds a docer image based on gunicorn for Django app
FROM python:3

# Copy project files
COPY ./entrypoint.sh /
COPY ./requirements.txt  /requirements.txt

# install required packages via PIP
RUN --mount=type=cache,target=/root/.cache \
    pip install -r /requirements.txt -U

# Copy project files
ADD  src/ /opt/src/

# Set a work dir
WORKDIR /opt/src/
ENV PYTHONUNBUFFERED=1

# Tell the docker which cmd to run when using this image
ENTRYPOINT ["sh", "/entrypoint.sh"]
