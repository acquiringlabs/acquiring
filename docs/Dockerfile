# Dockerfile for serving MkDocs documentation
FROM python:3.12-slim

WORKDIR /app

# Install MkDocs and any necessary plugins
RUN pip install mkdocs mkdocs-material

# Expose default MkDocs port
EXPOSE 8000

# Copy the content of the current directory into the container
COPY ./mkdocs.yml ./mkdocs.yml
COPY ./docs ./docs

# Serve the documentation
CMD ["mkdocs", "serve", "-a", "0.0.0.0:8000"]
