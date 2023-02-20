from django.urls import path
from .views import VideoList, CreateVideo, DetailVideo, UpdateVideo, DeleteVideo, ProfileView, SearchVideo, VideoDashboard, UpdateProfileView
from . import views

urlpatterns = [
    path('', VideoList.as_view(), name='home'),
    path('create/', CreateVideo.as_view(), name = 'video-create'),
    path('video/<slug:slug>/', DetailVideo.as_view(), name = 'video-detail'),
    path('video/<slug:slug>/update', UpdateVideo.as_view(), name = 'video-update'),
    path('video/<slug:slug>/delete', DeleteVideo.as_view(), name = 'video-delete'),
    path('profile/@<str:username>/', ProfileView.as_view(), name='profile'),
    path('update-profile/<str:username>/', UpdateProfileView.as_view(), name='update-profile'),
    path('video/search', SearchVideo.as_view(), name='search'),
    path('dashboard/@<str:username>/', VideoDashboard.as_view(), name = 'dashboard'),
    # path('activate/<int:user_id>/<str:uuid>/', activate_user, name='activate_user')
]