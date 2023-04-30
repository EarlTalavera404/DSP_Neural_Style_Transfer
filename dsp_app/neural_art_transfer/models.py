from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import magic



# Built-in file validator to only accepy png,jpg and jpeg files in the uploads
extension_validator = FileExtensionValidator(['png','jpg','jpeg'])

#Function which validates the files uploaded
def validate_filetype(file):
    #Create an array which only accepts png,jpeg and jpg files
    accept = ['image/png','image/jpeg','image/jpg']
    #Actually check that the contents of the files match their file type and the user didnt just rename the file to suit the file type
    file_type = magic.from_buffer(file.read(1024),mime=True)
    print(file_type)
    if file_type not in accept:
        raise ValidationError(" Unsupported file type ")#Display a message to the user that their file type is not suitable

#Table for the images model in the database with the user_id,image_id and image name
class Images(models.Model):
    user_id = models.ForeignKey(User,null=False,blank=True,on_delete=models.CASCADE)
    image_id = models.AutoField(primary_key=True)
    image = models.FileField(upload_to="content_images/",null=True, validators=[extension_validator,validate_filetype])

#Table for the algorithm model in the database with the user_id,algorithm_choices and algorithm name
class AlgorithmPreference(models.Model):
    user_id = models.ForeignKey(User,null=False,blank=True,on_delete=models.CASCADE)
    algorithm_choices = (('Original', 'Original'), ('Histogram', 'Histogram'), ('Normalised', 'Normalised'), ('Combined', 'Combined'))
    algorithm = models.CharField(max_length=10, choices=algorithm_choices,blank=True )

#Table for the style images model in the database with the user_id,image_id and image name
class StyleImage(models.Model):
    user_id = models.ForeignKey(User,null=False,blank=True,on_delete=models.CASCADE)
    image_id = models.AutoField(primary_key=True)
    image_style = models.FileField(upload_to="style_images/",null=True, validators=[extension_validator,validate_filetype])
