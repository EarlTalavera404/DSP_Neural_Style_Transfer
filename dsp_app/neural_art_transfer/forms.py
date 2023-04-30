from django import forms
from django.contrib.auth.forms import *
from django.contrib.auth.models import User
from neural_art_transfer.models import *


#This is for the login form 
class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email","password",)

#This is for the register form 
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','first_name', 'last_name', 'email', 'password1', 'password2']
        
#This is for the content image form 
class ImageForm(forms.ModelForm):
     class Meta:
        model = Images
        fields = ["image","user_id"]
        widgets = {
            'image':forms.FileInput(attrs={'accept':'.png,jpg,.jpeg'})#Used for validation on only accepting png,jpeg and jpg files
        }
#This is for the style image form form 
class StyleImageForm(forms.ModelForm):
     class Meta:
        model = StyleImage
        fields = ["image_style","user_id"]
        widgets = {
            'image_style':forms.FileInput(attrs={'accept':'.png,jpg,.jpeg'})#Used for validation on only accepting png,jpeg and jpg files
        }
        
#This is for the algorithm preference form 
class AlgorithmPreferenceForm(forms.ModelForm):
    class Meta:
        model=AlgorithmPreference
        fields = ["user_id","algorithm"]

