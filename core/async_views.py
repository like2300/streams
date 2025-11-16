# core/async_views.py
import os
import uuid
import asyncio
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.conf import settings
from .models import Video, Photo
import boto3
from botocore.exceptions import ClientError


@csrf_exempt
@require_http_methods(["POST"])
async def async_upload_video(request):
    """
    Vue asynchrone pour l'upload de vidéos vers R2
    """
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            category_id = request.POST.get('category')
            duration = request.POST.get('duration', 0)
            
            # Récupération du fichier vidéo
            video_file = request.FILES.get('video_file')
            cover_image = request.FILES.get('cover_image')
            
            if not video_file:
                return JsonResponse({'error': 'Aucun fichier vidéo fourni'}, status=400)
            
            # Génération d'un nom de fichier unique
            video_filename = f"videos/{uuid.uuid4().hex}_{video_file.name}"
            cover_filename = f"covers/{uuid.uuid4().hex}_{cover_image.name}" if cover_image else None
            
            # Upload asynchrone vers R2
            video_url = await upload_to_r2_async(video_file, video_filename)
            cover_url = await upload_to_r2_async(cover_image, cover_filename) if cover_image else None
            
            # Création de l'objet Video avec les URLs
            video = Video.objects.create(
                title=title,
                description=description,
                video_file=video_url,
                cover_image=cover_url,
                duration=int(duration),
                category_id=category_id if category_id else None
            )
            
            return JsonResponse({
                'success': True,
                'video_id': video.id,
                'video_url': video.video_url,
                'cover_url': video.cover_url
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


@csrf_exempt
@require_http_methods(["POST"])
async def async_upload_photo(request):
    """
    Vue asynchrone pour l'upload de photos vers R2
    """
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            category_id = request.POST.get('category')
            
            # Récupération du fichier image
            image_file = request.FILES.get('image_file')
            
            if not image_file:
                return JsonResponse({'error': 'Aucun fichier image fourni'}, status=400)
            
            # Génération d'un nom de fichier unique
            image_filename = f"photos/{uuid.uuid4().hex}_{image_file.name}"
            
            # Upload asynchrone vers R2
            image_url = await upload_to_r2_async(image_file, image_filename)
            
            # Création de l'objet Photo avec l'URL
            photo = Photo.objects.create(
                title=title,
                description=description,
                image_file=image_url,
                category_id=category_id if category_id else None
            )
            
            return JsonResponse({
                'success': True,
                'photo_id': photo.id,
                'image_url': photo.image_url
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


async def upload_to_r2_async(file, filename):
    """
    Fonction asynchrone pour uploader un fichier vers R2
    """
    # Configuration du client S3 pour R2
    s3_client = boto3.client(
        's3',
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name='auto'
    )
    
    try:
        # Lecture du contenu du fichier
        file_content = file.read()
        
        # Upload asynchrone vers R2
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: s3_client.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=filename,
                Body=file_content,
                ContentType=file.content_type
            )
        )
        
        # Retour de l'URL du fichier
        return f"{settings.MEDIA_URL}{filename}"
    
    except ClientError as e:
        raise Exception(f"Erreur lors de l'upload vers R2: {e}")