# Fetch the official base image for Python
FROM python:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Check if DJANGO_VERSION is provided, and install Django and requirements/$ENVIRONMENT-django.txt it if applicable
ARG DJANGO_VERSION=""
ARG ENVIRONMENT
RUN if [ ! -z "$DJANGO_VERSION" ]; then pip install Django==$DJANGO_VERSION && pip install -r requirements/${ENVIRONMENT}-django; fi

# Install shared dependencies
COPY requirements/ /code/requirements/
RUN pip install -r requirements/$ENVIRONMENT.txt

# Copy the django-acquiring package and the test project into the container
COPY . /code/

# Expose the port Django will run on
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
