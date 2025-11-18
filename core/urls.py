from django.urls import path, include
from . import views

administration_patterns = [
    path('home', views.home, name='home'),

    # Publiques 
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
    path('photo/<int:photo_id>/', views.photo_detail, name='photo_detail'),

    # Upload pages
    path('upload/video/', views.upload_video_uppy, name='upload_video_uppy'),
    path('upload/photo/', views.upload_photo_uppy, name='upload_photo_uppy'),

    # Edition et suppression
    path('video/<int:video_id>/edit/', views.edit_video, name='edit_video'),
    path('video/<int:video_id>/delete/', views.delete_video, name='delete_video'),
    path('photo/<int:photo_id>/edit/', views.edit_photo, name='edit_photo'),
    path('photo/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),
    path('api/upload/replace/', views.ReplaceMediaView.as_view(), name='replace_media'),

    # API pour modification de contenu
    path('api/video/<int:video_id>/update/', views.update_video_api, name='update_video_api'),
    path('api/photo/<int:photo_id>/update/', views.update_photo_api, name='update_photo_api'),
    
    # Gestion du contenu utilisateur
    path('my-content/', views.user_content, name='user_content'),

    # API (upload + presigned + finalize)
    path('api/upload/file/', views.upload_file, name='upload_file'),  # Server-side upload
    path('api/upload/presign/', views.S3PresignView.as_view(), name='s3_presign'),  # Direct R2 presigned
    path('api/upload/finalize/', views.FinalizeUploadView.as_view(), name='finalize_upload'),  # Finalize metadata

]


user_patterns = [
    path('', views.index, name='index'),
    path('video/player/<int:pk>/', views.video_player, name='video_player'),

    # Like/Comment URLs
    path('video/<int:video_id>/like/', views.toggle_video_like, name='toggle_video_like'),
    path('video/<int:video_id>/comment/', views.add_video_comment, name='add_video_comment'),
    path('photo/<int:photo_id>/like/', views.toggle_photo_like, name='toggle_photo_like'),
    path('photo/<int:photo_id>/like-status/', views.get_photo_like_status, name='get_photo_like_status'),  # New URL for checking like status
    path('photo/<int:photo_id>/comment/', views.add_photo_comment, name='add_photo_comment'),
    path('photo/<int:photo_id>/comments/', views.get_photo_comments, name='get_photo_comments'),

    path('search/', views.search_results, name='search_results'),  

    path('video_user/', views.video_user, name='video_user'),
    path('photo_user/', views.photo_user, name='photo_user'),

    path("change-username/", views.change_username, name="change_username"),
]


urlpatterns = [
    path('administration/', include(administration_patterns)),
    path('', include(user_patterns)),
]