import os
import logging
import traceback
from app import app
from extensions import db
from models import Admin, Course, Location, TrialLesson, User, CourseReview, CourseTag, District, UserActivity, SiteSettings, News, NewsImage, NewsComment, NewsTag, NewsCategory

# Настройка расширенного логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_imported_modules():
    """Log information about imported modules for debugging"""
    import sys
    logger.debug("Imported modules:")
    for name, module in sys.modules.items():
        if module:
            logger.debug(f"Module {name} loaded from {getattr(module, '__file__', 'unknown location')}")

if __name__ == "__main__":
    try:
        logger.info("Starting Flask server...")

        # Log imported modules for debugging
        log_imported_modules()

        # Log Flask app configuration
        logger.debug("Flask app configuration:")
        logger.debug(f"Debug mode: {app.debug}")
        logger.debug(f"Testing mode: {app.testing}")
        logger.debug(f"Secret key set: {'Yes' if app.secret_key else 'No'}")
        logger.debug(f"Database URL configured: {'Yes' if app.config.get('SQLALCHEMY_DATABASE_URI') else 'No'}")

        # Initialize database tables
        with app.app_context():
            logger.info("Creating database tables...")
            db.create_all()
            logger.info("Database tables created successfully")

        # Ensure upload directory exists
        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        logger.info(f"Upload folder created/verified: {upload_folder}")

        # Create news uploads directory
        news_uploads = os.path.join(upload_folder, 'news')
        os.makedirs(news_uploads, exist_ok=True)
        logger.info(f"News uploads folder created/verified: {news_uploads}")

        logger.info("Attempting to start server on port 5000...")

        app.run(
            host="0.0.0.0",
            port=5000,
            debug=True
        )
    except ImportError as e:
        logger.error(f"Import error during server startup: {str(e)}")
        logger.error("Import traceback:")
        logger.error(traceback.format_exc())
        raise
    except Exception as e:
        logger.error(f"Error during server startup: {str(e)}")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        raise