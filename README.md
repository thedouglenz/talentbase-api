# Talentbase-api

Flask REST API for a multipurpose file/folder cloud storage system

## Installation

1. Clone the repository
1. Create a virtual environment `python -m venv .venv`
1. Activate the virtual environment `source .venv/bin/activate`
1. Install the dependencies `pip install -r requirements.txt`
1. Create a `.env` file in the root directory and add the following environment variables:
    ```
    SECRET_KEY=your_secret_key
    DATABASE_URL=your_database_url
    FLASK_DEBUG=True
    FLASK_JWT_SECRET_KEY=your_jwt_secret_key
    PORT=8000
    ```
1. Run the application: `python run.py`
