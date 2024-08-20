# Use a GDAL-enabled image with Python 3.11 as a parent image
FROM osgeo/gdal:alpine-normal-3.11.0

RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-wheel \
    && pip3 install --upgrade pip

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed Python packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the datasets and app files into the container at /app
COPY . .

# Expose the port that the app runs on
EXPOSE 5001

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]
