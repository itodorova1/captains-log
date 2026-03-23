# 1. Base Image: A lightweight version of Python
FROM python:3.13-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy only the requirements first (this makes future builds much faster)
COPY requirements.txt .

# 4. Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your app's code into the container
COPY . .

# 6. Expose the port that Streamlit uses
EXPOSE 8501

# 7. Command to run the application when the container starts
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]