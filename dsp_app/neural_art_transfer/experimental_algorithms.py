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
#This function loads in the image into tensorflow and ensures that the image datatype and properties is suitable for neural style transfer
def load_image(path_to_img):
  max_dim = 800
  img = tf.io.read_file(path_to_img)
  img = tf.image.decode_image(img, channels=3)
  img = tf.image.convert_image_dtype(img, tf.float32)

  shape = tf.cast(tf.shape(img)[:-1], tf.float32)
  long_dim = max(shape)
  scale = max_dim / long_dim

  new_shape = tf.cast(shape * scale, tf.int32)

  img = tf.image.resize(img, new_shape)
  img = img[tf.newaxis, :]
  return img


def histogram_equalizer(image_path):
    #1. Retrieve the image through the image_path passed in
    bgr_img = cv2.imread(image_path)
    #2. convert image from RGB to HSV
    hsv_img = cv2.cvtColor(bgr_img, cv2.COLOR_RGB2HSV)
    #3, Perform histogram equalisation on the value channel 
    # Calculate the normalised histogram
    # Mapped each pixel value on a lookup table
    # transform the pixel intensities are all uniformly distributed 
    hsv_img[:, :, 2] = cv2.equalizeHist(hsv_img[:, :, 2])
    #4. convert back to RGB color-space from HSV
    image = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)
    filename =str("histogram_image_" + str(uuid.uuid4()))
    histogrampathname = fr".\neural_art_transfer\static\neural_art_transfer\histogram_equalised_images\{filename}.jpg"
    cv2.imwrite(histogrampathname,image)
    #5. Display/return image for neural style transfer
    return histogrampathname


def colour_normaliser(image_path):
    #1. Retrieve the image through the image_path passed in
    img = cv2.imread(image_path)
    #2. create a numpy array to store each pixel inside 
    img_array = np.zeros((800,800))
    #3, Perform colour normalisation on the array on the binary values by maxing the pixel instensity for better contrast
    colour_normalised_image = cv.normalize(img,  img_array, 0, 255, cv.NORM_MINMAX)
    colournormaliserpathname = fr".\neural_art_transfer\static\neural_art_transfer\colour_normalised_images\colour_normalised_image{str(uuid.uuid4())}.jpg"
    cv2.imwrite(colournormaliserpathname,colour_normalised_image)# This one works
    #5. Display/return image for neural style transfer
    return colournormaliserpathname










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
    originalfilename_concat =str("generated_image_" + str(uuid.uuid4()))#Pass into the output page
    originalfilename = fr".\neural_art_transfer\static\neural_art_transfer\generated_images\{originalfilename_concat}.jpg"
    cv2.imwrite(originalfilename, cv2.cvtColor(np.squeeze(stylized_image)*255, cv2.COLOR_BGR2RGB))



    #5. Perform histogram equalization on the image for better contrast -> generate a new image
    #Histogram equalization on the content image 
    #Start timer here 
    histo_start = time.time()
    contrasted_image_path=histogram_equalizer(file_path)
    #Load in the image and format into a float tensor
    histogram_content_image = load_image(contrasted_image_path)
    #Style the contrasted image
    stylized_image_histogram = model(tf.constant(histogram_content_image), tf.constant(style_image))[0]
    histo_end = time.time()
    histo_time_elapsed=histo_end-histo_start
    histo_before_format=histo_time_elapsed
    histo_time_elapsed = "{:.2f}".format(histo_time_elapsed)
    #Create the new contrasted image
    histogramfilename_concat =str("histogram_neural_" + str(uuid.uuid4()))#Pass into the output page
    finalisedhistogramneural = fr".\neural_art_transfer\static\neural_art_transfer\histogram_neural_images\{histogramfilename_concat}.jpg"
    cv2.imwrite(finalisedhistogramneural,cv2.cvtColor(np.squeeze(stylized_image_histogram)*255, cv2.COLOR_BGR2RGB))

    #Retrieve the stylised image name
    #6. Perform colour normalisation on the image for better clarity and distinction of colours -> generate a new image
    normalised_start = time.time()
    coloured_norm_image_path=colour_normaliser(file_path)
    coloured_content_image = load_image(coloured_norm_image_path)
    stylized_image_normalised = model(tf.constant(coloured_content_image), tf.constant(style_image))[0]
    normalised_end = time.time()
    normalised_time_elapsed=normalised_end-normalised_start
    normalised_time_elapsed = "{:.2f}".format(normalised_time_elapsed)
    normalisedfilename_concat =str("colour_normalised_neural_" + str(uuid.uuid4()))#Pass into the output page
    finalisednormalisedimage = fr".\neural_art_transfer\static\neural_art_transfer\colour_normalised_neural_images\{normalisedfilename_concat}.jpg"
    cv2.imwrite(finalisednormalisedimage,cv2.cvtColor(np.squeeze(stylized_image_normalised)*255, cv2.COLOR_BGR2RGB))

    
    #7. Combine Histogram,equalizer and colour normalisation
    #Get histogram equalised image then colour normalise then neural style transfer!
    combined_start = time.time()
    combine_image_path=colour_normaliser(contrasted_image_path)
    combined_content_image = load_image(combine_image_path)
    stylized_image_combined = model(tf.constant(combined_content_image), tf.constant(style_image))[0]
    combined_end = time.time()
    combined_time_elapsed=combined_end-combined_start
    combined_before_format=combined_time_elapsed
    combined_time_elapsed=combined_before_format+histo_before_format
    combined_time_elapsed = "{:.2f}".format(combined_time_elapsed)
    combinedfilename_concat =str("combined_neural_" + str(uuid.uuid4()))#Pass into the output page
    combineneuralstyletransferpath = fr".\neural_art_transfer\static\neural_art_transfer\combined_neural_images\{combinedfilename_concat}.jpg"
    cv2.imwrite(combineneuralstyletransferpath,cv2.cvtColor(np.squeeze(stylized_image_combined)*255, cv2.COLOR_BGR2RGB))

    
    #Perform os.remove(path) to those 3 images but not the neural style transfer generated images
    #There should only be the media upload image, the original, histogram, colour normalised and combined: total of 5 images
    #Pass in the file to remove by first checking if the path exists
    path_list =[contrasted_image_path,coloured_norm_image_path,combine_image_path]
    # If file exists, delete it.
    for path in path_list:
        if os.path.isfile(path):
            os.remove(path)
        else:
            # If it is not found inform the user that the file is not found, 
            print("Error: %s file not found" % path_list[path])
            break
            

    return(originalfilename_concat,histogramfilename_concat,normalisedfilename_concat,combinedfilename_concat,histo_time_elapsed,normalised_time_elapsed,combined_time_elapsed)





@login_required
def image_input(request):
    #Instantiate an image form object
    image_form = ImageForm
    #Check if the request is a POST
    if request.method =='POST':
        #Instatiate the imageform with a file and post request
        image_form = ImageForm(request.POST, request.FILES)
        #Retrieve the user id of the user and attach it to the image the user has uploaded so they are tied to the user in the db
        image_form.fields['user_id'].initial=request.user
        uploaded_image = request.FILES['image']
        #Check if the form is valid
        if image_form.is_valid():
            image = image_form.save(commit=False)
            image.user_id=request.user
            #Save the form details
            image_form.save()
            #Pass in the style chosen from the html page and style the image according to the users choices
            if request.POST['Style_group'] == 'choice1': #DAVID HOCKNEY STYLE
                #Fast Neural Style Algorithm
                #Load in the tensor flow hub module which contains the pretrained dataset
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                #Start the timer for processing time
                start = time.time()
                #Pass in the content and style image into the fast style transfer algorithm
                image_name_tuple=fast_neural_algorithm(uploaded_image.name,'Hockney_workshop_crop.jpg')
                end = time.time()
                time_elapsed=end-start
                #End the timer
                time_elapsed = "{:.2f}".format(time_elapsed)
                #Format the image name paths from the tuple passed in through the fast_neural_algorithm
                original_image_name=str(image_name_tuple[0])+".jpg"
                histo_image_name=str(image_name_tuple[1])+".jpg"
                normalised_image_name=str(image_name_tuple[2])+".jpg"
                combined_image_name=str(image_name_tuple[3])+".jpg"
                #Format the pre-processing times from the tuple passed in through the fast_neural_algorithm
                histo_time_elapsed=str(image_name_tuple[4])
                normalised_time_elapsed=str(image_name_tuple[5])
                combined_time_elapsed=str(image_name_tuple[6])
                return redirect('image_output_experiment',original_image_name,histo_image_name,normalised_image_name,combined_image_name,time_elapsed,histo_time_elapsed,normalised_time_elapsed,combined_time_elapsed) # redirect the user to the output image page
            elif request.POST['Style_group'] == 'choice2': #BANKSY STYLE
                #Fast Neural Style Algorithm
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                image_name_tuple=fast_neural_algorithm(uploaded_image.name,'sfamous-banksy-paintings.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                original_image_name=str(image_name_tuple[0])+".jpg"
                histo_image_name=str(image_name_tuple[1])+".jpg"
                normalised_image_name=str(image_name_tuple[2])+".jpg"
                combined_image_name=str(image_name_tuple[3])+".jpg"

                histo_time_elapsed=str(image_name_tuple[4])
                normalised_time_elapsed=str(image_name_tuple[5])
                combined_time_elapsed=str(image_name_tuple[6])
                return redirect('image_output_experiment',original_image_name,histo_image_name,normalised_image_name,combined_image_name,time_elapsed,histo_time_elapsed,normalised_time_elapsed,combined_time_elapsed) # redirect the user to the output image page
            elif request.POST['Style_group'] == 'choice3': #J.M.W. TURNER STYLE
                #Fast Neural Style Algorithm
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                image_name_tuple=fast_neural_algorithm(uploaded_image.name,'JMW_Turner.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                original_image_name=str(image_name_tuple[0])+".jpg"
                histo_image_name=str(image_name_tuple[1])+".jpg"
                normalised_image_name=str(image_name_tuple[2])+".jpg"
                combined_image_name=str(image_name_tuple[3])+".jpg"

                histo_time_elapsed=str(image_name_tuple[4])
                normalised_time_elapsed=str(image_name_tuple[5])
                combined_time_elapsed=str(image_name_tuple[6])
                return redirect('image_output_experiment',original_image_name,histo_image_name,normalised_image_name,combined_image_name,time_elapsed,histo_time_elapsed,normalised_time_elapsed,combined_time_elapsed) # redirect the user to the output image page
            elif request.POST['Style_group'] == 'choice4':  #VAN GOGH STYLE
                #Fast Neural Style Algorithm
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                image_name_tuple=fast_neural_algorithm(uploaded_image.name,'vangogh.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                original_image_name=str(image_name_tuple[0])+".jpg"
                histo_image_name=str(image_name_tuple[1])+".jpg"
                normalised_image_name=str(image_name_tuple[2])+".jpg"
                combined_image_name=str(image_name_tuple[3])+".jpg"

                histo_time_elapsed=str(image_name_tuple[4])
                normalised_time_elapsed=str(image_name_tuple[5])
                combined_time_elapsed=str(image_name_tuple[6])
                return redirect('image_output_experiment',original_image_name,histo_image_name,normalised_image_name,combined_image_name,time_elapsed,histo_time_elapsed,normalised_time_elapsed,combined_time_elapsed) # redirect the user to the output image page
            elif request.POST['Style_group'] == 'choice5': #HOKUSAI STYLE
                #Fast Neural Style Algorithm
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                image_name_tuple=fast_neural_algorithm(uploaded_image.name,'The_Great_Wave_off_Kanagawa.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                original_image_name=str(image_name_tuple[0])+".jpg"
                histo_image_name=str(image_name_tuple[1])+".jpg"
                normalised_image_name=str(image_name_tuple[2])+".jpg"
                combined_image_name=str(image_name_tuple[3])+".jpg"

                histo_time_elapsed=str(image_name_tuple[4])
                normalised_time_elapsed=str(image_name_tuple[5])
                combined_time_elapsed=str(image_name_tuple[6])
                return redirect('image_output_experiment',original_image_name,histo_image_name,normalised_image_name,combined_image_name,time_elapsed,histo_time_elapsed,normalised_time_elapsed,combined_time_elapsed) # redirect the user to the output image page
            elif request.POST['Style_group'] == 'choice6': #FRIDA KAHLO STYLE
                #Fast Neural Style Algorithm
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                image_name_tuple=fast_neural_algorithm(uploaded_image.name,'FridaKahlo_Self-portrait_with_Hummingbird_and_Thorn-Necklace.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                original_image_name=str(image_name_tuple[0])+".jpg"
                histo_image_name=str(image_name_tuple[1])+".jpg"
                normalised_image_name=str(image_name_tuple[2])+".jpg"
                combined_image_name=str(image_name_tuple[3])+".jpg"

                histo_time_elapsed=str(image_name_tuple[4])
                normalised_time_elapsed=str(image_name_tuple[5])
                combined_time_elapsed=str(image_name_tuple[6])
                return redirect('image_output_experiment',original_image_name,histo_image_name,normalised_image_name,combined_image_name,time_elapsed,histo_time_elapsed,normalised_time_elapsed,combined_time_elapsed) # redirect the user to the output image page

            elif request.POST['Style_group'] == 'choice7': #PICASSO STYLE
                #Fast Neural Style Algorithm
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                image_name_tuple=fast_neural_algorithm(uploaded_image.name,'picasso.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                original_image_name=str(image_name_tuple[0])+".jpg"
                histo_image_name=str(image_name_tuple[1])+".jpg"
                normalised_image_name=str(image_name_tuple[2])+".jpg"
                combined_image_name=str(image_name_tuple[3])+".jpg"

                histo_time_elapsed=str(image_name_tuple[4])
                normalised_time_elapsed=str(image_name_tuple[5])
                combined_time_elapsed=str(image_name_tuple[6])
                return redirect('image_output_experiment',original_image_name,histo_image_name,normalised_image_name,combined_image_name,time_elapsed,histo_time_elapsed,normalised_time_elapsed,combined_time_elapsed) # redirect the user to the output image page
            elif request.POST['Style_group'] == 'choice8': #MARCO MAZZONI STYLE
                #Fast Neural Style Algorithm
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                image_name_tuple=fast_neural_algorithm(uploaded_image.name,'MarcoMazzoni_05.jpg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                original_image_name=str(image_name_tuple[0])+".jpg"
                histo_image_name=str(image_name_tuple[1])+".jpg"
                normalised_image_name=str(image_name_tuple[2])+".jpg"
                combined_image_name=str(image_name_tuple[3])+".jpg"

                histo_time_elapsed=str(image_name_tuple[4])
                normalised_time_elapsed=str(image_name_tuple[5])
                combined_time_elapsed=str(image_name_tuple[6])
                return redirect('image_output_experiment',original_image_name,histo_image_name,normalised_image_name,combined_image_name,time_elapsed,histo_time_elapsed,normalised_time_elapsed,combined_time_elapsed) # redirect the user to the output image page
            elif request.POST['Style_group'] == 'choice9': #LEONARDO DA VINCI STYLE
                #Fast Neural Style Algorithm
                model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
                start = time.time()
                image_name_tuple=fast_neural_algorithm(uploaded_image.name,'LEONARDO.jpeg')
                end = time.time()
                time_elapsed=end-start
                time_elapsed = "{:.2f}".format(time_elapsed)
                original_image_name=str(image_name_tuple[0])+".jpg"
                histo_image_name=str(image_name_tuple[1])+".jpg"
                normalised_image_name=str(image_name_tuple[2])+".jpg"
                combined_image_name=str(image_name_tuple[3])+".jpg"

                histo_time_elapsed=str(image_name_tuple[4])
                normalised_time_elapsed=str(image_name_tuple[5])
                combined_time_elapsed=str(image_name_tuple[6])
                return redirect('image_output_experiment',original_image_name,histo_image_name,normalised_image_name,combined_image_name,time_elapsed,histo_time_elapsed,normalised_time_elapsed,combined_time_elapsed) # redirect the user to the output image page
            else:
                #If the user didnt choose a style an error message is displayed to the console
                #Not required since the style choice is a required field
                print("You didnt choose an style to apply!")
        else:

            print("Form invalid ")
    #Pass in the image form into the html
    context = {
        'image_form': image_form,
     }
    

    #Render the html along with the form
    return render(request ,'neural_art_transfer/experimental_stylise_input.html',context)
