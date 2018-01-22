
FROM rapydo/celery:0.6.0
# FROM openjdk:8-jre-alpine

# ###################
# RUN apk update && apk add python3 git postgresql-dev
# # py3-psycopg2
# # install celery
# # RUN wget --no-check-certificate https://bootstrap.pypa.io/get-pip.py \
# #     && python get-pip.py && rm *.py
# COPY requirements.txt /tmp/
# WORKDIR /tmp
# RUN for package in `cat requirements.txt`; do \
#     echo "adding: $package"; pip3 install --upgrade --no-cache-dir $package; done
# # RUN pip install --upgrade --force-reinstall --no-cache-dir -r /tmp/requirements.txt

# ENV RAPYDO_VERSION 0.6.0
# RUN pip3 install --upgrade --no-cache-dir git+https://github.com/rapydo/utils.git@$RAPYDO_VERSION
# RUN pip3 install --upgrade --no-cache-dir git+https://github.com/rapydo/http-api.git@$RAPYDO_VERSION

###################
RUN apt-get install -y openjdk-8-jre

###################
# Make a directory for inputs (will be mounted into here):
RUN mkdir -p /usr/local/opt/readonly/ && mkdir -p /usr/local/opt/readwrite/
# Note: Only readwrite is used,
#but both must exist because both will be mounted!

# Get the java code:
COPY ./unzip.jar /usr/src/unzip/
WORKDIR /usr/src/unzip
# Run java code to unzip:
CMD java -jar unzip.jar /usr/local/opt/readwrite/${FILENAME}
