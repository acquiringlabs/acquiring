# Dockerfile for serving MkDocs documentation
FROM python:3.12-slim

WORKDIR /app

# Install MkDocs and any necessary plugins
RUN pip install mkdocs mkdocs-material

# Expose default MkDocs port
EXPOSE 8008

# Copy the content of the current directory into the container
COPY ./mkdocs.yml ./mkdocs.yml
COPY ./docs ./docs
COPY ./material ./material

# Serve the documentation
CMD ["mkdocs", "serve", "--dev-addr", "0.0.0.0:8008", "--watch-theme"]
