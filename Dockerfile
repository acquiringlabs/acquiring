# Fetch the official base image for Python
FROM python:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code
COPY requirements/ /code/requirements/

# Check if DJANGO_VERSION is provided,
# And install Django, the shared dependencies and requirements/$ENVIRONMENT-django.txt
# Otherwise install just the shared dependencies
ARG DJANGO_VERSION=""
ARG ENVIRONMENT
RUN if [ ! -z "$DJANGO_VERSION" ]; then pip install Django==$DJANGO_VERSION && pip install -r requirements/${ENVIRONMENT}-django.txt; else pip install -r requirements/$ENVIRONMENT.txt; fi

# Copy the acquiring package and the test project into the container
COPY . /code/

# Expose the port Django will run on
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
