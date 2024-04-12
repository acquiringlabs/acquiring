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
ARG SQLALCHEMY_VERSION=""
ARG ENVIRONMENT

# Install Django, SQLAlchemy, and other dependencies
RUN INSTALL_CMD=""; \
    if [ ! -z "$DJANGO_VERSION" ]; then \
        INSTALL_CMD="${INSTALL_CMD} Django==$DJANGO_VERSION -r requirements/${ENVIRONMENT}-django.txt "; \
    fi; \
    if [ ! -z "$SQLALCHEMY_VERSION" ]; then \
        INSTALL_CMD="${INSTALL_CMD} SQLAlchemy==$SQLALCHEMY_VERSION -r requirements/${ENVIRONMENT}-sqlalchemy.txt "; \
    fi; \
    if [ ! -z "$INSTALL_CMD" ]; then \
        pip install $INSTALL_CMD; \
    else \
        pip install -r requirements/$ENVIRONMENT.txt; \
    fi;


# Copy the acquiring package and the test project into the container
COPY . /code/

# Expose the port Django will run on
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
