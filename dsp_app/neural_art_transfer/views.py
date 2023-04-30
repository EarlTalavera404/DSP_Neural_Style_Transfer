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
from .models import *

import matplotlib.pyplot as plt
from io import StringIO
import numpy as np
import os




@login_required
def display_graph(request):
    #Pie chart of ratings distribution of user
    user_votes_data = []
    #Retrieve the sum of all the user votes on the original algorithm
    standard_count = AlgorithmPreference.objects.filter(algorithm="Original").count()
    #Retrieve the sum of all the user votes on the histogram equalised algorithm
    histogram_count = AlgorithmPreference.objects.filter(algorithm="Histogram").count()
    #Retrieve the sum of all the user votes on the colour normalised algorithm
    normalised_count = AlgorithmPreference.objects.filter(algorithm="Normalised").count()
    #Retrieve the sum of all the user votes on the combined algorithm
    combined_count = AlgorithmPreference.objects.filter(algorithm="Combined").count()
    #Append the retrieve votes into a list 
    user_votes_data.append(standard_count)
    user_votes_data.append(histogram_count)
    user_votes_data.append(normalised_count)
    user_votes_data.append(combined_count)


    #Save the votes list into the context to be rendered in the html
    context ={
              "user_votes_data":user_votes_data
              }
    return render(request, 'neural_art_transfer/preference_graph.html', context)





#login function,changed the name to login_user so we could use the inbuilt login function
def login_user(request):
    #Check if the request is a POST
    if request.method =="POST":
        #Retrieve the email and password inputted by the user in the form
        email = request.POST.get('email')
        password = request.POST.get('password')
        #Authenticate the username and password by cross-matching in the database
        user=authenticate(request,username=email,password=password)
        #Check if the user exists in the database if so render the home page else display an error message and ask to try again
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            error_message = "Invalid username or password"
            context = {
                "error_message":error_message
            }
            return render(request, 'neural_art_transfer/login.html',context)
    else:
        return render(request, 'neural_art_transfer/login.html')         

#Allows users to register into the database 
def register(request):
    #Instantiate the register form
    user_form = CreateUserForm()
    #Check if the request is a POST
    if request.method == 'POST':
        user_form = CreateUserForm(request.POST)
        #Check if the details inputted in the form is valid
        if user_form.is_valid():
            #Save the form but not fully since we need to add the user to the base user group
            user_form.save(commit=False)
            #Retrieve the group of Base User
            group = Group.objects.get(name='Base_User')
            #Save the user into the Base User group
            user=user_form.save()
            user.groups.add(group)
            #Redirect the user back the login page
            return redirect(login_user)
        #Else display an error messag e that their register was unsuccessful 
        else:
            error_message = "Invalid Credentials"
            context = {
                "error_message":error_message,
                'user_form': user_form
            }
            return render(request, 'neural_art_transfer/register.html',context)
    
    
    return render(request, 
                  'neural_art_transfer/register.html', 
                  {'user_form': user_form})


#logout function redirect back to login page
@login_required
def logout_user(request):
    logout(request)
    return redirect("login")


#Renders the home page of the website
def home(request):
    return render(request, 'neural_art_transfer/home.html', )


#Displays the generated image to the user and allows them to see the time elapsed aswell as the choice to delete their uploaded images
@login_required
def image_output(request,image_name,time_elapsed):
    #Format the image name to the appropiate path
    image_name_path=fr".\neural_art_transfer\static\neural_art_transfer\generated_images\{str(image_name)}"\
    #Check if the request is a POST
    if request.method =='POST':
        #Check if the user clicked the delete button
        if request.POST.get("delete_image"):
            #Delete the content image and style image(arbitrary only) uploaded aswell (for loop in case the user has any images that is still stored)
            user=request.user
            id=user.id
            content_image_obj= Images.objects.filter(user_id=id)
            style_image_obj= StyleImage.objects.filter(user_id=id) 
            for cont_img in content_image_obj:
                cont_img.delete()
            for style_img in style_image_obj:
                style_img.delete()
            #Delete the generated image
            if os.path.isfile(image_name_path):
                os.remove(image_name_path)
                print("Successfully deleted")
                return redirect("home")
            else:
                # If it is not found inform the user that the file is not found, 
                print("Error: %s file not found" % image_name_path)
                return redirect("home")
        
                
            
    #Pass in the image name and the time elapsed for the algorithm to run to the htlm
    context ={
        "image_name":image_name,
        "time_elapsed":time_elapsed

    }
    
    return render(request ,'neural_art_transfer/image_output.html',context)

#Displays to the user the 4 generated images as well as the elapsed time and a choice to pick the most preferred algorithm
@login_required
def image_output_experiment(request,original_image_name,histo_image_name,normalised_image_name,combined_image_name,time_elapsed,histo_time_elapsed,normalised_time_elapsed,combined_time_elapsed):
    # Retrieve the image paths and format it to retrieve the generated images
    org_image_name_path=fr".\neural_art_transfer\static\neural_art_transfer\generated_images\{str(original_image_name)}"
    his_image_name_path=fr".\neural_art_transfer\static\neural_art_transfer\histogram_neural_images\{str(histo_image_name)}"
    nor_image_name_path=fr".\neural_art_transfer\static\neural_art_transfer\colour_normalised_neural_images\{str(normalised_image_name)}"
    com_image_name_path=fr".\neural_art_transfer\static\neural_art_transfer\combined_neural_images\{str(combined_image_name)}"
    #Append the formated image paths to a list
    path_list=(org_image_name_path,his_image_name_path,nor_image_name_path,com_image_name_path)
    #Instantiate the algorithm preference form
    algorithm_form = AlgorithmPreferenceForm
    #Check if the request is a POST
    if request.method =='POST':
        algorithm_form = AlgorithmPreferenceForm(request.POST)
        algorithm_form.fields['user_id'].initial=request.user
        print(algorithm_form.fields['user_id'])
        #If the form is valid then we can check which algorithm they picked
        if algorithm_form.is_valid():
            if request.POST['algorithm_choice'] == 'original':
                preference = algorithm_form.save(commit=False)
                #We save their algorithm choice as Original in the database
                preference.algorithm='Original'
                preference.user_id=request.user
                algorithm_form.save()
                #Delete the content image + generated images 
                user=request.user
                id=user.id
                content_image_obj_list= Images.objects.filter(user_id=id)
                for image_element in content_image_obj_list:
                    image_element.delete()
                #Delete generated Images
                for paths in path_list:
                    if os.path.isfile(paths):
                        os.remove(paths)
                        print("Successfully deleted")
                    else:
                        # If it is not found inform the user that the file is not found, 
                        print("Error: %s file not found" % paths)
    
                return redirect("home")
                
            elif request.POST['algorithm_choice'] == 'histogram_equalised':
                preference = algorithm_form.save(commit=False)
                #We save their algorithm choice as Histogram in the database
                preference.algorithm='Histogram'
                preference.user_id=request.user
                algorithm_form.save()
                #Delete the content image + generated images 
                user=request.user
                id=user.id
                content_image_obj_list= Images.objects.filter(user_id=id)
                for image_element in content_image_obj_list:
                    image_element.delete()
                #Delete Generated Images
        
                for paths in path_list:
                    if os.path.isfile(paths):
                        os.remove(paths)
                        print("Successfully deleted")
                    else:
                        # If it is not found inform the user that the file is not found, 
                        print("Error: %s file not found" % paths)
                return redirect('home')

            elif request.POST['algorithm_choice'] == 'colour_normalised':
                preference = algorithm_form.save(commit=False)
                #We save their algorithm choice as Normalised in the database
                preference.algorithm='Normalised'
                preference.user_id=request.user
                algorithm_form.save()
                #Delete the content image + generated images 
                user=request.user
                id=user.id
                content_image_obj_list= Images.objects.filter(user_id=id)
                for image_element in content_image_obj_list:
                    image_element.delete()
                #Delete Generated Images
                 #Delete the generated image
                for paths in path_list:
                    if os.path.isfile(paths):
                        os.remove(paths)
                        print("Successfully deleted")
                    else:
                        # If it is not found inform the user that the file is not found, 
                        print("Error: %s file not found" % paths)
                return redirect('home')

            elif request.POST['algorithm_choice'] == 'combined':
                preference = algorithm_form.save(commit=False)
                #We save their algorithm choice as Combined in the database
                preference.algorithm='Combined'
                preference.user_id=request.user
                algorithm_form.save()
                #Delete the content image + generated images 
                user=request.user
                id=user.id
                content_image_obj_list= Images.objects.filter(user_id=id)
                for image_element in content_image_obj_list:
                    image_element.delete()
                #Delete Generated Images
                for paths in path_list:
                    if os.path.isfile(paths):
                        os.remove(paths)
                        print("Successfully deleted")
                    else:
                        # If it is not found inform the user that the file is not found, 
                        print("Error: %s file not found" % paths)
                return redirect('home')
            else:   
                print("Your preference form is invalid!")
                return redirect('/')
        else:
            print("Not valid")
            return redirect('/')
        

    context ={
        "algorithm_form":algorithm_form,
        "original_image_name":original_image_name,
        "histo_image_name":histo_image_name,
        "normalised_image_name":normalised_image_name,
        "combined_image_name":combined_image_name,
        "time_elapsed":time_elapsed,
        "histo_time_elapsed":histo_time_elapsed,
        "normalised_time_elapsed":normalised_time_elapsed,
        "combined_time_elapsed":combined_time_elapsed,

    }
    return render(request ,'neural_art_transfer/experimental_stylise_output.html',context)


#Allows the users to view any content and style images on the website which they have not deleted
@login_required
def view_images(request):
    #Retrieve the current user id 
    get_user=request.user
    id=get_user.id
    user=User.objects.get(pk=id)
    #Retrieve the images stored in the database belonging to the user by checking if the image user id matches their id
    images_content_objects= Images.objects.filter(user_id=user)
    images_style_objects= StyleImage.objects.filter(user_id=user) 
   
    #Pass in the list of images into the html to be displayed to the user
    context = {
        "images_content_objects":images_content_objects,
        "images_style_objects":images_style_objects,
    }

    return render(request,'neural_art_transfer/view_images.html',context)



#Deletes the content image belong to the user from the database 
@login_required
def delete_content_image(request,image):
    #Check if any images exists
    if image:
        #Retrieve the image which the user clicked on and delete it
        image_obj = Images.objects.get(image_id=image)
        image_obj.delete()
    # Redirect back to the table.
    return redirect('view_images')

#Deletes the style image belong to the user from the database 
@login_required
def delete_style_image(request,image):
    #Check if any images exists
    if image:
        #Retrieve the image which the user clicked on and delete it
        image_obj = StyleImage.objects.get(image_id=image)
        image_obj.delete()
    # Redirect back to the table.
    return redirect('view_images')


#Allows the manager to view all base users in the database
@login_required
@allowed_users(allowed_roles=['Manager'])
def view_users(request):
    #Retrieve all base users in the database
    users=User.objects.filter(groups__name='Base_User')
    #Pass the list to the html
    context = {
        "users":users
    }

    return render(request,'neural_art_transfer/view_users.html',context)




#Allows the manager to delete base users in the database
@login_required
@allowed_users(allowed_roles=['Manager'])
def delete_user(request,user_id):
    if user_id:
        #Passes in the base user_id the manager clicked on 
        user_obj = User.objects.get(id=user_id)
        #Delete in the base user from the database
        user_obj.delete()
    # Redirect back to the table.
    return redirect('view_users')
