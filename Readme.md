### Project Setup Documentation

#### 1. Setting Up Python and Virtual Environment
 - Set up a virtual environment : 
```bash
python -m venv videoproject_venv
source videoproject_venv/bin/activate  
```

#### 2. Install Required Packages
 - Install Django and other required packages from a `requirements.txt` file.
    - Install the dependencies using pip:
        ```bash
        pip install -r requirements.txt
        ```

#### 3. Initialize the Database
 - Perform initial migrations to set up database schema:
```bash
python manage.py migrate
```

#### Running Tests
 - For running all the test Cases
```bash
python manage.py test
```

#### Running the API Server
- To start the API server
```bash
python manage.py runserver
```
This command starts a lightweight development web server on the local machine. Navigating to `http://127.0.0.1:8000/` in your web browser.


#### Viewing API Documentation
- If you have set up Swagger or Redoc with `drf-yasg`, you can view your API documentation by visiting:
    - Swagger UI: `http://127.0.0.1:8000/swagger/`
    - Redoc: `http://127.0.0.1:8000/redoc/`

