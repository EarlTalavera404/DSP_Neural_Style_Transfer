from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from . import fast_algorithm
from . import experimental_algorithms

#URL patterns for the views and respective htmls
urlpatterns = [
    path('login/', views.login_user, name="login"),
    path('logout', views.logout_user, name="logout"),
    path('register', views.register, name="register"),
    path('display_preference',views.display_graph, name="display_preference"),
    path('view_images', views.view_images,name="view_images"),
    path('view_users', views.view_users, name="view_users"),
    path('delete_user/<int:user_id>', views.delete_user, name="delete_user"),
    path('delete_content_image/<str:image>', views.delete_content_image, name="delete_content_image"),
    path('delete_style_image/<str:image>', views.delete_style_image, name="delete_style_image"),
    path('image_input_arbitrary',fast_algorithm.image_input_arbitrary,name="image_input_arbitrary"),
    path('image_input', fast_algorithm.image_input, name="image_input"),
    path('image_input_experiment', experimental_algorithms.image_input, name="image_input_experiment"),
    path('image_output/<str:image_name>/<str:time_elapsed>', views.image_output, name="image_output"),
    path('image_output_experiment/<str:original_image_name>/<str:histo_image_name>/<str:normalised_image_name>/<str:combined_image_name>/<str:time_elapsed>/<str:histo_time_elapsed>/<str:normalised_time_elapsed>/<str:combined_time_elapsed>', views.image_output_experiment, name="image_output_experiment"),
    path('', views.home, name="home")

] 

