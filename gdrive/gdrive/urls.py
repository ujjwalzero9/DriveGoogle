from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import UserViewSet, EntityViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'entities', EntityViewSet)

# Define a custom URL pattern for creating a user
urlpatterns = [
    path('admin/', admin.site.urls),
    path('create_user/', UserViewSet.as_view({'post': 'create'}), name='create_user'),
    path('create_entity/', EntityViewSet.as_view({'post': 'create'}), name='create_entity'),
    path('get_folder_contents/', EntityViewSet.as_view({'post': 'get_folder_contents'}), name='get_folder_contents'),
    path('delete_folder/', EntityViewSet.as_view({'post': 'delete_folder'}), name='delete_folder'),
    path('users/login/', UserViewSet.as_view({'post': 'login'}), name='user-login'),
    path('presigned-url/', UserViewSet.as_view({'post': 'get_presigned_url'}), name='get-presigned-url'),
    path('', include(router.urls)),  # Include all router-generated URLs
]
