from django.db import models
from django.contrib.auth.models import User 
from PIL import Image



class Profile_User(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self):
        super().save()
        img = Image.open(self.image.path)
        thumbnail_output_image_size = (300, 300)
        thumbnail_max_size = 300
        original_width, original_height = img.size

        if original_width > 300 and original_height > 300:
            # Calculate the scaling factor for width and height
            thumbnail_width_scale = thumbnail_max_size / original_width
            thumbnail_height_scale = thumbnail_max_size / original_height
            
            # Choose the smaller of the two scales to maintain aspect ratio
            thumbnail_scale = min(thumbnail_width_scale, thumbnail_height_scale)
            
            # Calculate the new dimensions
            thumbnail_new_width = int(original_width * thumbnail_scale)
            thumbnail_new_height = int(original_height * thumbnail_scale)

            # Resize the image
            thumbnail_img = img.resize((thumbnail_new_width, thumbnail_new_height), Image.Resampling.LANCZOS)
            
            thumbnail_img_width, thumbnail_img_heigh = thumbnail_img.size
            thumb_center_x = thumbnail_img_width / 2
            thumb_center_y = thumbnail_img_heigh / 2
            
            # Calculate cropping box coordinates for thumbnail
            left = thumb_center_x - thumbnail_output_image_size[0] / 2
            top = thumb_center_y - thumbnail_output_image_size[1] / 2
            right = thumb_center_x + thumbnail_output_image_size[0] / 2
            bottom = thumb_center_y + thumbnail_output_image_size[1] / 2
            # Crop the image
            thumbnail_img = thumbnail_img.crop((left, top, right, bottom))
            thumbnail_img.save(self.image.path)