# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /myproject

# Copy the requirements file into the container
COPY requirements.txt /myproject/

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the Django app code to the container
COPY . /myproject/

# RUN python manage.py makemigrations
# RUN python manage.py migrate
# Install dependencie

# Expose the port on which the Django app will run
EXPOSE 8000

# Update the CMD to run uWSGI for your application
CMD ["gunicorn", "geo_search_api.wsgi:application", "--bind", "0.0.0.0:8000"]
