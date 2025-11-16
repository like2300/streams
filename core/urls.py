from django.urls import path
from . import views

urlpatterns = [
    # Publiques
    path('', views.home, name='home'),
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
    path('photo/<int:photo_id>/', views.photo_detail, name='photo_detail'),

    # Upload pages
    path('upload/video/', views.upload_video_uppy, name='upload_video_uppy'),
    path('upload/photo/', views.upload_photo_uppy, name='upload_photo_uppy'),

    # API (upload + presigned + finalize)
    path('api/upload/file/', views.upload_file, name='upload_file'),  # Server-side upload
    path('api/upload/presign/', views.S3PresignView.as_view(), name='s3_presign'),  # Direct R2 presigned
    path('api/upload/finalize/', views.FinalizeUploadView.as_view(), name='finalize_upload'),  # Finalize metadata
]