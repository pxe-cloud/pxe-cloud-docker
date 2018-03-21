# Use Alpine Linux as base image
FROM alpine:3.7

# Install all the required packages
RUN apk add --update --no-cache rethinkdb

# Expose the required ports
EXPOSE 29015
EXPOSE 28015
EXPOSE 8080

# Run the service
CMD [ "rethinkdb", "--directory", "/data", "--bind", "all" ]