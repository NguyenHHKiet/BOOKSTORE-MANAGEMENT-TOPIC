
import cloudinary.uploader
def save_picture(form_picture):
    response = cloudinary.uploader.upload(form_picture)
    return response['secure_url']
