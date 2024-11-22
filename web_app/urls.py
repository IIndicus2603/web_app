"""
URL configuration for photo_slider project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
# photo_slider/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from images import views

urlpatterns = [
    path('', views.image_slider, name='index'),  # Ensure 'image_slider' is the correct name
    path('upload/', views.image_upload, name='image_upload'),
    path('check_duplicate/', views.image_check_duplicate, name='image_check_duplicate'),
    path('update_tag/', views.update_tag, name='update_tag'),
    path('add_tag/', views.add_tag, name='add_tag'),  # Thêm dòng này
    path('delete_tag/', views.delete_tag, name='delete_tag'),  # Thêm dòng này
    path('cleanup/', views.cleanup, name='cleanup'),
    path('get_image_tags/', views.get_image_tags, name='get_image_tags'),

]

# Cung cấp các file media trong môi trường phát triển
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)