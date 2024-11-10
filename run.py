import os
from app import create_app

from dotenv import load_dotenv


load_dotenv()

app = create_app()

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', True), port=os.getenv('PORT', 5000))