from app import create_app
import logging

app = create_app()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)