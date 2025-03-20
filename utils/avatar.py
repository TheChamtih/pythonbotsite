import os
from PIL import Image
from werkzeug.utils import secure_filename
import uuid

AVATAR_UPLOAD_FOLDER = "static/uploads/avatars"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_SIZE = (500, 500)

# Create avatar upload directory if it doesn't exist
os.makedirs(AVATAR_UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_avatar(file):
    """
    Сохраняет загруженный аватар, оптимизирует его размер и возвращает имя файла
    """
    if file and allowed_file(file.filename):
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(AVATAR_UPLOAD_FOLDER, filename)
        
        # Optimize and save image
        try:
            image = Image.open(file)
            image.thumbnail(MAX_SIZE)
            image.save(filepath, quality=85, optimize=True)
            return filename
        except Exception as e:
            print(f"Error saving avatar: {e}")
            return None
    return None
