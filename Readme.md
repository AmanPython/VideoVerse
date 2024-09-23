# VideoProject Documentation

## Project Overview

VideoProject is a robust backend service crafted using Django and Django REST framework, designed to manage video files through a range of functionalities including uploading, trimming, merging, and generating shareable links with expiration settings. It leverages Celery for asynchronous tasks and Redis for message queuing. Adhering to best practices in API development, error handling, and code quality, it provides comprehensive API documentation accessible via Swagger.

- [Frontend Repository](https://github.com/AmanPython/Frontend)

## Key Features

1. **Authenticated API Calls**: Utilizes static API tokens for authentication.
2. **Video Upload**: Supports file uploads with limits on size and duration.
3. **Video Trimming**: Offers video trimming from the beginning or end.
4. **Video Merging**: Allows merging of multiple video clips into one.
5. **Link Sharing with Expiry**: Creates shareable links that expire over time.
6. **Testing**: Implements unit and end-to-end testing to verify system integrity.
   ```bash
   git fetch
   git checkout -b testing origin/testing
   python manage.py test
   ```
7. **API Documentation**: Available via Swagger UI.

## System Requirements

- Python 3.12.3
- Django 5.1.1
- SQLite (Database)
- Redis (Message broker for Celery)
- Celery (Task queue)
- Django REST Framework
- drf-yasg (For API documentation)

## Project Setup

### Python and Virtual Environment

Initialize a virtual environment to manage package dependencies separately.

```bash
# Creating a virtual environment
python -m venv videoproject_venv
# Activating the virtual environment
source videoproject_venv/bin/activate
```

### Dependencies Installation

Install Django and necessary libraries from the `requirements.txt`.

```bash
pip install -r requirements.txt
```

### Database Initialization

Execute migrations to configure the database schema.

```bash
python manage.py migrate
```

### Testing the Application

Run the test suite to ensure everything is functioning correctly.

```bash
python manage.py test
```

### Launching the API Server

Deploy the local development server:

```bash
python manage.py runserver
```

Access the server at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

### Configuring Celery

Initialize Celery worker and scheduler:

```bash
# Worker
celery -A videoproject worker --loglevel=info
# Scheduler
celery -A videoproject beat --loglevel=info
```

### Redis Configuration

Set up Redis to manage Celery tasks:

1. Install Redis:

    ```bash
    sudo apt update
    sudo apt install redis-server
    ```

2. Start and verify Redis service:

    ```bash
    sudo systemctl start redis.service
    sudo systemctl status redis
    ```

### API Documentation Access

View the API documentation hosted locally:

- **Swagger UI**: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
- **Redoc**: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

### Third-Party Integrations

- **JWT Authentication**: [JWT Authentication documentation](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/).
- **Swagger Documentation**: [drf-yasg integration guide](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/drf_yasg_integration.html).


## Reference Material

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery](https://docs.celeryq.dev/en/stable/)
- [Redis](https://redis.io/documentation)
- [Pillow](https://pillow.readthedocs.io/en/stable/)
- [Imageio-ffmpeg](https://ffmpeg.org/)
- [Imageio](https://imageio.readthedocs.io/en/stable/)
- [MoviePy](https://zulko.github.io/moviepy/)