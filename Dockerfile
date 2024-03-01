# Fetch the official base image for Python
FROM python:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements/ /code/requirements/

ARG ENVIRONMENT
ARG DJANGO_VERSION
RUN pip install Django==$DJANGO_VERSION && pip install -r requirements/$ENVIRONMENT.txt

# Copy the django-acquiring package and the test project into the container
COPY . /code/

# Expose the port Django will run on
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
