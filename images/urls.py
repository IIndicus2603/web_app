# images/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.image_slider, name='index'),  # Ensure 'image_slider' is the correct name
    path('upload/', views.image_upload, name='image_upload'),
    path('check_duplicate/', views.image_check_duplicate, name='image_check_duplicate'),
    path('update_tag/', views.update_tag, name='update_tag'),
    path('add_tag/', views.add_tag, name='add_tag'),
    path('delete_tag/', views.delete_tag, name='delete_tag'),
    path('cleanup/', views.cleanup, name='cleanup'),
    path('get_image_tags/', views.get_image_tags, name='get_image_tags'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)