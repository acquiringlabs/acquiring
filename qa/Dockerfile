# Fetch the official base image for Python
FROM python:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code
COPY requirements.txt /code/requirements.txt

ARG DJANGO_VERSION
ARG ACQUIRING_VERSION

RUN pip install -r requirements.txt
RUN pip install Django==$DJANGO_VERSION acquiring==${ACQUIRING_VERSION}

COPY wait-for-it.sh /wait-for-it.sh
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]


# Copy the acquiring package and the test project into the container
COPY . /code/

# Expose the port Django will run on
EXPOSE 8888

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8888"]
