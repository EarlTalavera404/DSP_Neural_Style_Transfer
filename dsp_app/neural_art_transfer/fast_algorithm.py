from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate,logout #Import for the authenticate feature for login and logout
from django.contrib import messages#Display messages on the webpages in response to events
from django.contrib.auth.models import Group #Import groups for user types
from .decorators import * #Import all user type decorators for use
from django.contrib.auth.decorators import login_required #Blocks function based on whether the user is logged in
from .forms import *
from .decorators import *

import tensorflow_hub as hub
import tensorflow as tf
from matplotlib import pyplot as plt
import numpy as np
import cv2
import os
import uuid
import cv2 as cv
import time

#Perform image resize to maximise the clarity of the output aswell as minimise the processing power required -> generate a new image
def load_image(path_to_img):
  max_dim = 800
  img = tf.io.read_file(path_to_img)
  img = tf.image.decode_image(img, channels=3)
  img = tf.image.convert_image_dtype(img, tf.float32)
  shape = tf.cast(tf.shape(img)[:-1], tf.float32)
  long_dim = max(shape)
  if long_dim > max_dim: #Checks the size of the image and if it is smaller than the max dimension we can leave the size as it is
    scale = max_dim / long_dim
    shape = tf.cast(tf.shape(img)[:-1], tf.float32)
    long_dim = max(shape)
    scale = max_dim / long_dim
    new_shape = tf.cast(shape * scale, tf.int32)
    img = tf.image.resize(img, new_shape,preserve_aspect_ratio=True)
    img = img[tf.newaxis, :]
    return img
  else:
    img = tf.io.read_file(path_to_img)
    img = tf.image.decode_image(img, channels=3)
    img = tf.image.convert_image_dtype(img, tf.float32)
    img = img[tf.newaxis, :]
    return img




def fast_neural_algorithm(content_image_name,style_image_name):
    #1. Import the model from tensorflow hub
    model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
    #2.Load the content and style images inside the respective static folders
    media_folder = './media/content_images/'
    file_path=f"{media_folder}{content_image_name}"
    content_image= load_image(file_path)
    format_path = fr'.\neural_art_transfer\static\neural_art_transfer\style_images\{style_image_name}'
    style_image = load_image(format_path) 
    #3.Stylise the content image
    stylized_image = model(tf.constant(content_image), tf.constant(style_image))[0]
    #4.Generate the output image and put it into the generated folder, also make sure to generate a random string 
    # to prevent the image from being overwritten!
    filename =str("generated_image_" + str(uuid.uuid4()))
    originalfilename = fr".\neural_art_transfer\static\neural_art_transfer\generated_images\{filename}.jpg"
    # originalfilename = fr"C:\Users\talav\Desktop\DSP Project\DSP_Neural_Style_Transfer\dsp_app\neural_art_transfer\static\neural_art_transfer\generated_images\{filename}.jpg"
    cv2.imwrite(originalfilename, cv2.cvtColor(np.squeeze(stylized_image)*255, cv2.COLOR_BGR2RGB))
    return str(filename)
     
    
def fast_neural_algorithm_arbitrary(content_image_name,style_image_name):
    #1. Import the model from tensorflow hub
    model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
    #2.Load the content and style images inside the respective static folders
    media_folder = './media/content_images/'
    file_path=f"{media_folder}{content_image_name}"
    content_image= load_image(file_path)
    media_folder_style = './media/style_images/'
    file_path_style=f"{media_folder_style}{style_image_name}"
    style_image = load_image(file_path_style) 
    #3.Stylise the content image
    stylized_image = model(tf.constant(content_image), tf.constant(style_image))[0]
    #4.Generate the output image and put it into the generated folder, also make sure to generate a random string 
    # to prevent the image from being overwritten!
    filename =str("generated_image_" + str(uuid.uuid4()))
    originalfilename = fr".\neural_art_transfer\static\neural_art_transfer\generated_images\{filename}.jpg"
    # originalfilename = fr"C:\Users\talav\Desktop\DSP Project\DSP_Neural_Style_Transfer\dsp_app\neural_art_transfer\static\neural_art_transfer\generated_images\{filename}.jpg"
    cv2.imwrite(originalfilename, cv2.cvtColor(np.squeeze(stylized_image)*255, cv2.COLOR_BGR2RGB))
    return str(filename)
   
   

@login_required
def image_input(request):
    image_form = ImageForm
    if request.method =='POST':
        image_form = ImageForm(request.POST, request.FILES)
        # image_form.user_id=request.user.
        image_form.fields['user_id'].initial=request.user.id
        print(image_form.fields['user_id'])
        uploaded_image = request.FILES['image']
        # print(uploaded_image.name)
        if image_form.is_valid():
            # print(request.user.id)
            image = image_form.save(commit=False)
            image.user_id=request.user
            # print(image_form)
            image_form.save()
            if request.POST['Style_group'] == 'choice1': #DAVID HOCKNEY STYLE
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                #Time the function here
                start = time.time()
                output_path=fast_neural_algorithm(uploaded_image.name,'Hockney_workshop_crop.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                # time_elapsed=str(time_elapsed)
                # print(output_path)
                image_name=output_path+".jpg"
                # print(image_name) testing this out for image name
                return redirect('image_output',image_name,time_elapsed) # redirect the user to the output image 
            elif request.POST['Style_group'] == 'choice2': #BANKSY STYLE
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                output_path=fast_neural_algorithm(uploaded_image.name,'sfamous-banksy-paintings.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                image_name=output_path+".jpg"
                return redirect('image_output',image_name,time_elapsed) # redirect the user to the output image 
            elif request.POST['Style_group'] == 'choice3': #J.M.W. TURNER STYLE
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                output_path=fast_neural_algorithm(uploaded_image.name,'JMW_Turner.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                image_name=output_path+".jpg"
                return redirect('image_output',image_name,time_elapsed) # redirect the user to the output image 
            elif request.POST['Style_group'] == 'choice4':  #VAN GOGH STYLE
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                output_path=fast_neural_algorithm(uploaded_image.name,'vangogh.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                image_name=output_path+".jpg"
                return redirect('image_output',image_name,time_elapsed) # redirect the user to the output image 
            elif request.POST['Style_group'] == 'choice5': #HOKUSAI STYLE
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                output_path=fast_neural_algorithm(uploaded_image.name,'The_Great_Wave_off_Kanagawa.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                image_name=output_path+".jpg"
                return redirect('image_output',image_name,time_elapsed) # redirect the user to the output image 
            elif request.POST['Style_group'] == 'choice6': #FRIDA KAHLO STYLE
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                output_path=fast_neural_algorithm(uploaded_image.name,'FridaKahlo_Self-portrait_with_Hummingbird_and_Thorn-Necklace.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                image_name=output_path+".jpg"
                return redirect('image_output',image_name,time_elapsed) # redirect the user to the output image 
            elif request.POST['Style_group'] == 'choice7': #PICASSO STYLE
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                output_path=fast_neural_algorithm(uploaded_image.name,'picasso.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                image_name=output_path+".jpg"
                return redirect('image_output',image_name,time_elapsed) # redirect the user to the output image 
            elif request.POST['Style_group'] == 'choice8': #MARCO MAZZONI STYLE
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                output_path=fast_neural_algorithm(uploaded_image.name,'MarcoMazzoni_05.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                image_name=output_path+".jpg"
                return redirect('image_output',image_name,time_elapsed) # redirect the user to the output image 
            elif request.POST['Style_group'] == 'choice9': #LEONARDO DA VINCI STYLE
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                output_path=fast_neural_algorithm(uploaded_image.name,'LEONARDO.jpeg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                image_name=output_path+".jpg"
                return redirect('image_output',image_name,time_elapsed) # redirect the user to the output image 
            else:
                print("You didnt choose an style to apply!")
        else:
            
            print("Form invalid ")
  
    context = {
        'image_form': image_form,
        'user':request.user.id
      
        
     }
    

    return render(request ,'neural_art_transfer/image_input.html',context)


#Similar algorithm but allows the user to input their own style image
@login_required
def image_input_arbitrary(request):
    image_form = ImageForm
    style_image_form = StyleImageForm
    if request.method =='POST':
        #Create an instance of the image form(the content image the user uploads)
        content_image_form = ImageForm(request.POST, request.FILES)
        #Create an instance of the style image form(the style image the user uploads)
        style_image_form = StyleImageForm(request.POST,request.FILES)
        #Bind the upload content image with the user id of the user that is uploading ut
        content_image_form.fields['user_id'].initial=request.user.id
        print(content_image_form.fields['user_id'])
        uploaded_image = request.FILES['image'] 
        
        #Bind the upload style image with the user id of the user that is uploading it
        style_image_form.fields['user_id'].initial=request.user.id
        style_upload_image = request.FILES['image_style']
        # print(uploaded_image.name)
        if content_image_form.is_valid() and style_image_form.is_valid():
            # print(request.user.id)
            #Save the instance of the content image and set the user id with it
            image = content_image_form.save(commit=False)
            image.user_id=request.user
            # print(image_form)
            content_image_form.save()
            #Save the instance of the style image and set the user id with it
            style_image=style_image_form.save(commit=False)
            style_image.user_id=request.user
            style_image_form.save()
            model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
            #Time the function here
            start = time.time()
            output_path=fast_neural_algorithm_arbitrary(uploaded_image.name,style_upload_image.name)
            end = time.time()
            time_elapsed=end-start
            time_elapsed = "{:.2f}".format(time_elapsed)
            #Pass in the image path to display the image
            image_name=output_path+".jpg"
            return redirect('image_output',image_name,time_elapsed) # redirect the user to the output image 
        else:
            print("Form invalid ")
    #Pass in the content and style image form and the user id in the html
    context = {
        'image_form': image_form,
        'style_image_form':style_image_form,
        'user':request.user.id   
     }
    #Render the html with the context
    return render(request ,'neural_art_transfer/image_input_arbitrary.html',context)
