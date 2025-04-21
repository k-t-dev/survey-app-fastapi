# Step 1: Use the official Python image as the base
FROM python:3.10-slim

# Step 2: Set the working directory in the container
WORKDIR /backend

# Step 3: Copy requirements file to the working directory
COPY requirements.txt .

# Step 4: Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the application code to the container
# COPY ./backend /backend
COPY . /backend

# Step 6: Expose the FastAPI application port
EXPOSE 5009

# Step 7: Start FastAPI using uvicorn
CMD ["uvicorn", "App.main:app", "--host", "0.0.0.0", "--port", "5009"]


##RUN
# docker build -t fastapi-app_2 . 
#docker run -d -p 5009:5009 fastapi-app_2