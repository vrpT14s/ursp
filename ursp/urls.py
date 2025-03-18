"""
URL configuration for ursp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from booking import views as booking_views

urlpatterns = [
    path('', booking_views.index, name="home"),
    path('login/', booking_views.login, name="login"),
    path('login/create', booking_views.create_user, name="create_user"),
    path('login/post', booking_views.login_post, name="login_post"),
    path('admin/', admin.site.urls),
    path('res/', booking_views.view_resources, name="view_resources"),
    path('res/create', booking_views.create_resource, name="create_resource"),
    path('res/<int:resource_id>/book', booking_views.book_resource, name="book_resource"),
    path('res/<int:resource_id>/book/post', booking_views.book_resource_post, name="book_resource_post"),
    path('res/<int:resource_id>/feedback', booking_views.feedback, name="feedback"),
    path('res/<int:resource_id>/feedback/post', booking_views.feedback_post, name="feedback_post"),
]
