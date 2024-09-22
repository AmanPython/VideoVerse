# VideoProject

## Project Overview

VideoProject is a backend service that provides REST APIs for handling video files, including uploading, trimming, merging, and generating shareable links with expiration. The project is built using Django and Django REST framework and utilizes Celery for asynchronous task processing and Redis as a message broker. This project follows best practices for API design, exception handling, and code quality, with comprehensive API documentation available through Swagger.

## Features

1. **Authenticated API Calls**: All API requests are authenticated using static API tokens.
2. **Video Upload**: Users can upload video files with configurable limits on file size and duration.
3. **Video Trimming**: Trim videos from the start or end based on user specifications.
4. **Video Merging**: Merge multiple video clips into a single file.
5. **Link Sharing with Expiry**: Generate shareable links with time-based expiry.
6. **Testing**: Unit and end-to-end tests ensure the robustness of the application.
7. **API Documentation**: Available through Swagger UI.

## Requirements

- Python 3.12.3
- Django 5.1.1
- SQLite (Database)
- Redis (For Celery message broker)
- Celery (Task queue)
- Django REST Framework
- drf-yasg (for API documentation)

## Project Setup Documentation

### 1. Setting Up Python and Virtual Environment

Set up a virtual environment to isolate dependencies.

```bash
# Create a virtual environment
python -m venv videoproject_venv
# or
python3 -m venv videoproject_venv

# Activate the virtual environment
source videoproject_venv/bin/activate
```

### 2. Install Required Packages

Install Django and other required packages listed in the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 3. Initialize the Database

Run initial migrations to set up the database schema.

```bash
python manage.py migrate
```

### Running Tests

To run all test cases:

```bash
python manage.py test
```

### Running the API Server

Start the API server:

```bash
python manage.py runserver
```

This command starts a lightweight development web server on the local machine. You can access it at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

### Running Celery and Celery-beat

Start Celery worker:

```bash
celery -A videoproject worker --loglevel=info
```

Start Celery beat scheduler:

```bash
celery -A videoproject beat --loglevel=info
```

### Redis Setup

Redis is used as a message broker for Celery tasks.

1. Install Redis:

    ```bash
    sudo apt update
    sudo apt install redis-server
    ```

2. Start Redis:

    ```bash
    sudo systemctl start redis.service
    sudo systemctl status redis  # Check Redis status
    ```

### Viewing API Documentation

If you have set up Swagger or Redoc with drf-yasg, you can view the API documentation by visiting:

- **Swagger UI**: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
- **Redoc**: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

### 3rd Party APIs

- **JWT Authentication**: Refer to the [JWT Authentication documentation](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/).
- **Swagger Documentation Integration**: For integrating Swagger with Django, see the [drf-yasg integration guide](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/drf_yasg_integration.html).

## Assumptions and Choices

- **Static API Tokens**: For simplicity, static API tokens are used for authentication instead of OAuth.
https://github.com/AmanPython/VideoVerse/blob/bd168c0b14f6be01e8aeab3175ffb7e0d67bec48/videoproject/settings.py#L69-L82

- **File Size and Duration Limits**: Configurable limits were set to ensure that server resources are managed effectively.
https://github.com/AmanPython/VideoVerse/blob/bd168c0b14f6be01e8aeab3175ffb7e0d67bec48/videoapi/serializers.py#L18-L41

- **SQLite Database**: 
https://github.com/AmanPython/VideoVerse/blob/bd168c0b14f6be01e8aeab3175ffb7e0d67bec48/videoproject/settings.py#L103-L112

- **Error Handling**: Thorough error handling with descriptive messages to guide users in correcting their requests.

## Submission Guidelines

- Ensure the repository has a clear commit history reflecting the development process.
- The README should provide setup commands, test suite execution instructions, and commands to run the API server.

## References

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryq.dev/en/stable/)
- [Redis Documentation](https://redis.io/documentation)

For any questions or issues, please refer to the documentation links or raise an issue in the repository.



 #### Authenticated API Calls  
 
 #### Video Upload 
 #### Video Trimming  
 #### Video Merging 
 #### Link Sharing with Expiry 
 #### Testing 
 #### API Documentation