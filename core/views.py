import json
import logging
import uuid
import re
import os
import boto3
from botocore.config import Config
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.files.uploadedfile import UploadedFile
from django.contrib import messages
from .forms import VideoForm, PhotoForm, PhotoEditForm, VideoEditForm
from .models import Video, Photo, Category
 

logger = logging.getLogger(__name__)

# =====================================================================
# VUES PUBLIQUES
# =====================================================================

def home(request):
    videos = Video.objects.all()[:6]
    photos = Photo.objects.all()[:6]
    return render(request, 'core/index.html', {'videos': videos, 'photos': photos})

def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    video.views += 1
    video.save()
    return render(request, 'core/video_detail.html', {'video': video})

def photo_detail(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    return render(request, 'core/photo_detail.html', {'photo': photo})

# =====================================================================
# VUES UPLOAD PAGE
# =====================================================================

@login_required
def upload_video_uppy(request):
    categories = Category.objects.all()
    return render(request, 'core/upload_video_uppy.html', {'categories': categories})

@login_required
def upload_photo_uppy(request):
    categories = Category.objects.all()
    return render(request, 'core/upload_photo_uppy.html', {'categories': categories})

# =====================================================================
# API VIEWS - SERVER-SIDE UPLOAD TO R2
# =====================================================================

@csrf_exempt
def upload_file(request):
    """Upload file to R2 via server-side (bypasses CORS issues with direct R2 uploads)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        uploaded_file = request.FILES.get('file')
        upload_type = request.POST.get('uploadType', 'files')
        
        if not uploaded_file:
            return JsonResponse({'error': 'No file provided'}, status=400)

        # Create a unique filename
        original_name = uploaded_file.name
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', original_name)
        unique_name = f"{uuid.uuid4().hex[:12]}_{safe_name}"
        key = f"{upload_type}/{unique_name}"

        # Upload to R2
        s3 = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='auto'
        )

        s3.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=key,
            Body=uploaded_file.read(),
            ContentType=uploaded_file.content_type or 'application/octet-stream'
        )

        # Construct the public URL using CDN or fallback
        cdn = getattr(settings, 'R2_CDN_DOMAIN', '') or os.getenv('R2_CDN_DOMAIN', '').strip()
        if cdn and cdn.startswith("http"):
            public_root = cdn.rstrip('/')
        elif cdn:
            public_root = f"https://{cdn.rstrip('/')}"
        else:
            public_root = f"{settings.AWS_S3_ENDPOINT_URL.rstrip('/')}/{settings.AWS_STORAGE_BUCKET_NAME}"
        
        file_url = f"{public_root}/{key}"
        
        return JsonResponse({
            'success': True,
            'fileURL': file_url,
            'key': key
        })

    except Exception as e:
        logger.error("Error uploading file: %s", e, exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

# =====================================================================
# API VIEWS - PRESIGNED UPLOAD (DIRECT R2) - FALLBACK OPTION
# =====================================================================

@method_decorator(csrf_exempt, name='dispatch')
class S3PresignView(View):
    """Génère un presigned POST compatible R2 et retourne une public_url pour construire le lien final côté client."""
    def post(self, request):
        try:
            # Parse JSON body (Uppy sends JSON, not form-data)
            data = json.loads(request.body)
            filename = data.get('filename', '').strip()
            content_type = data.get('contentType', '').strip()
            upload_type = data.get('uploadType', 'photos').strip()

            if not filename:
                return JsonResponse({'error': 'Filename manquant'}, status=400)

            # safe + unique filename
            safe = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
            unique = f"{uuid.uuid4().hex[:12]}_{safe}"
            key = f"{upload_type}/{unique}"

            s3 = boto3.client(
                's3',
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name='auto',
                config=Config(signature_version='s3v4', s3={'addressing_style': 'path'})
            )

            # Generate presigned POST for R2 with explicit R2-compatible parameters
            presigned = s3.generate_presigned_post(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=key,
                Fields={
                    "Content-Type": content_type or "application/octet-stream",
                    "key": key  # Include the key in the form fields as required by S3-compatible services
                },
                Conditions=[
                    {"Content-Type": content_type or "application/octet-stream"},
                    ["content-length-range", 1, 2 * 1024**3],  # 1 byte to 2GB
                    ["starts-with", "$key", key]  # The key should match exactly
                ],
                ExpiresIn=3600  # 1 hour
            )

            # Construct the public URL using CDN if available (this is for accessing files after upload)
            cdn = getattr(settings, 'R2_CDN_DOMAIN', '') or os.getenv('R2_CDN_DOMAIN', '').strip()
            if cdn and cdn.startswith("http"):
                public_root = cdn.rstrip('/')
            elif cdn:
                public_root = f"https://{cdn.rstrip('/')}"
            else:
                # Fallback - should use the CDN domain if available, otherwise use the endpoint with bucket
                public_root = f"{settings.AWS_S3_ENDPOINT_URL.rstrip('/')}/{settings.AWS_STORAGE_BUCKET_NAME}"

            return JsonResponse({
                'url': presigned['url'],  # Upload URL (R2 endpoint with bucket in path)
                'fields': presigned['fields'],  # Form fields to include in POST
                'method': 'POST',
                'key': key,  # Key for this specific upload
                'public_root': public_root,  # Base URL for public access after upload
                'bucket_name': settings.AWS_STORAGE_BUCKET_NAME
            })
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error("Erreur presign: %s", e, exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class FinalizeUploadView(View):
    """Sauvegarde métadonnées (fileURL attendu public)"""
    def post(self, request):
        try:
            data = json.loads(request.body or "{}")
            file_url = data.get('fileURL')
            cover_image = data.get('cover_image')
            upload_type = data.get('uploadType', 'photo')
            title = data.get('title', '').strip()
            description = data.get('description', '').strip()
            category_id = data.get('category')
            duration = data.get('duration', 0)

            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Non authentifié'}, status=401)
            if not file_url or not title:
                return JsonResponse({'error': 'URL ou titre manquant'}, status=400)

            if upload_type == 'video':
                video = Video.objects.create(
                    user=request.user,
                    title=title,
                    description=description,
                    video_file=file_url,
                    cover_image=cover_image,
                    duration=int(duration) if duration else 0,
                    category_id=category_id if category_id else None,
                )
                return JsonResponse({'success': True, 'id': video.id, 'url': f'/administration/video/{video.id}/', 'message': 'Vidéo publiée'})
            elif upload_type == 'photo':
                photo = Photo.objects.create(
                    user=request.user,
                    title=title,
                    description=description,
                    photo_file=file_url,
                    category_id=category_id if category_id else None,
                )
                return JsonResponse({'success': True, 'id': photo.id, 'url': f'/administration/photo/{photo.id}/', 'message': 'Photo publiée'})

            return JsonResponse({'error': 'Type invalide'}, status=400)
        except Exception as e:
            logger.error("Erreur finalisation: %s", e, exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)


# =====================================================================
# VUES MODIFICATION ET SUPPRESSION
# =====================================================================
@login_required
def edit_video(request, video_id):
    """Affiche le formulaire de modification pour une vidéo existante."""
    video = get_object_or_404(Video, id=video_id)
    
    # Vérifier que l'utilisateur est le propriétaire
    if request.user != video.user and not request.user.is_staff:
        messages.error(request, "Vous n'avez pas l'autorisation de modifier cette vidéo.")
        return redirect('video_detail', video_id=video_id)
    
    categories = Category.objects.all()
    
    if request.method == 'POST':
        # Utiliser le nouveau formulaire qui n'a pas de champ fichier
        form = VideoEditForm(request.POST, instance=video)
        
        if form.is_valid():
            # Sauvegarder les métadonnées
            form.save()
            
            # Gérer les URLs mises à jour provenant du JavaScript
            cover_image_url = request.POST.get('cover_image_url')
            video_file_url = request.POST.get('video_file_url')
            
            # Mettre à jour les champs avec les nouvelles URLs si elles sont fournies
            if cover_image_url:
                video.cover_image = cover_image_url
                print(f"Nouvelle URL de couverture: {cover_image_url}")  # Debug
            if video_file_url:
                video.video_file = video_file_url
                print(f"Nouvelle URL de vidéo: {video_file_url}")  # Debug
                
            # Sauvegarder les modifications
            video.save()
            
            messages.success(request, "Vidéo mise à jour avec succès !")
            return redirect('video_detail', video_id=video_id)
    else:
        # Si GET, pré-remplir le formulaire
        form = VideoEditForm(instance=video)
    
    return render(request, 'core/edit_video.html', {
        'form': form, 
        'video': video, 
        'categories': categories,
        'api_replace_url': request.build_absolute_uri(reverse('replace_media')) # URL pour notre API de remplacement
    })

@login_required
def delete_video(request, video_id):
    '''Vue pour supprimer un vidéo'''
    video = get_object_or_404(Video, id=video_id)
    
    # Vérifier que l'utilisateur est le propriétaire
    if request.user != video.user and not request.user.is_staff:
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer cette vidéo.")
        return render(request, 'core/video_detail.html', {'video': video})
    
    if request.method == 'POST':
        video_title = video.title
        video.delete()
        messages.success(request, f"Vidéo '{video_title}' supprimée avec succès!")
        return redirect(reverse('home'))  # Rediriger vers la page d'accueil après suppression
    
    return render(request, 'core/delete_video.html', {'video': video})

 

@login_required
def edit_photo(request, photo_id):
    """Affiche le formulaire de modification pour une photo existante."""
    photo = get_object_or_404(Photo, id=photo_id)
    
    # Vérifier que l'utilisateur est le propriétaire
    if request.user != photo.user and not request.user.is_staff:
        messages.error(request, "Vous n'avez pas l'autorisation de modifier cette photo.")
        return redirect(reverse('photo_detail', kwargs={'photo_id': photo_id}))
    
    categories = Category.objects.all()
    
    if request.method == 'POST':
        # Utilisez le NOUVEAU formulaire qui n'a pas de champ fichier
        form = PhotoEditForm(request.POST, instance=photo)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Photo mise à jour avec succès !")
            return redirect(reverse('photo_detail', kwargs={'photo_id': photo_id}))
    else:
        # Si GET, pré-remplit le formulaire avec les données existantes
        form = PhotoEditForm(instance=photo)
    
    return render(request, 'core/edit_photo.html', {
        'form': form, 
        'photo': photo, 
        'categories': categories,
        'api_replace_url': request.build_absolute_uri(reverse('replace_media'))
    })


@login_required
def delete_photo(request, photo_id):
    '''Vue pour supprimer une photo'''
    photo = get_object_or_404(Photo, id=photo_id)
    
    # Vérifier que l'utilisateur est le propriétaire
    if request.user != photo.user and not request.user.is_staff:
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer cette photo.")
        return render(request, 'core/photo_detail.html', {'photo': photo})
    
    if request.method == 'POST':
        photo_title = photo.title
        photo.delete()
        messages.success(request, f"Photo '{photo_title}' supprimée avec succès!")
        return redirect(reverse('home'))  # Rediriger vers la page d'accueil après suppression
    
    return render(request, 'core/delete_photo.html', {'photo': photo})


# =====================================================================
# VUES POUR GÉRER LE CONTENU UTILISATEUR
# =====================================================================

@login_required
def user_content(request):
    '''Vue pour afficher le contenu de l'utilisateur'''
    videos = Video.objects.filter(user=request.user).order_by('-created_at')
    photos = Photo.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'core/user_content.html', {
        'videos': videos,
        'photos': photos
    })


# =====================================================================
# API VIEWS - MODIFICATION VIA API (SIMILAIRE À LA CRÉATION)
# =====================================================================

@method_decorator(csrf_exempt, name='dispatch')
class UpdateVideoAPIView(View):
    '''API pour modifier une vidéo via l'API (comme la création mais sans upload direct)'''
    def post(self, request, video_id):
        try:
            video = get_object_or_404(Video, id=video_id)
            
            # Vérifier les permissions
            if request.user != video.user and not request.user.is_staff:
                return JsonResponse({'error': 'Accès refusé'}, status=403)
            
            data = json.loads(request.body or "{}")
            
            # Mettre à jour les métadonnées
            video.title = data.get('title', video.title)
            video.description = data.get('description', video.description)
            video.duration = int(data.get('duration', video.duration)) if data.get('duration') else video.duration
            
            # Mettre à jour la catégorie
            category_id = data.get('category')
            if category_id and str(category_id).isdigit():
                video.category = get_object_or_404(Category, id=int(category_id))
            else:
                video.category = None
            
            # Mettre à jour les URLs si fournies
            if 'new_video_url' in data and data['new_video_url']:
                video.video_file = data['new_video_url']
            if 'new_cover_url' in data and data['new_cover_url']:
                video.cover_image = data['new_cover_url']
                
            video.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Vidéo mise à jour avec succès',
                'video_url': f'/video/{video.id}/'
            })
        except Exception as e:
            logger.error("Erreur modification vidéo API: %s", e, exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class UpdatePhotoAPIView(View):
    '''API pour modifier une photo via l'API (comme la création mais sans upload direct)'''
    def post(self, request, photo_id):
        try:
            photo = get_object_or_404(Photo, id=photo_id)
            
            # Vérifier les permissions
            if request.user != photo.user and not request.user.is_staff:
                return JsonResponse({'error': 'Accès refusé'}, status=403)
            
            data = json.loads(request.body or "{}")
            
            # Mettre à jour les métadonnées
            photo.title = data.get('title', photo.title)
            photo.description = data.get('description', photo.description)
            
            # Mettre à jour la catégorie
            category_id = data.get('category')
            if category_id and str(category_id).isdigit():
                photo.category = get_object_or_404(Category, id=int(category_id))
            else:
                photo.category = None
                
            # Mettre à jour l'URL de la photo si fournie
            if 'new_photo_url' in data and data['new_photo_url']:
                photo.photo_file = data['new_photo_url']
                
            photo.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Photo mise à jour avec succès',
                'photo_url': f'/photo/{photo.id}/'
            })
        except Exception as e:
            logger.error("Erreur modification photo API: %s", e, exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)


# Fonctions utilitaires pour les vues classiques
update_video_api = UpdateVideoAPIView.as_view()
update_photo_api = UpdatePhotoAPIView.as_view()

@method_decorator(csrf_exempt, name='dispatch')
class ReplaceMediaView(View):
    """
    Vue API générique pour uploader un fichier média (cover, photo, vidéo, etc.)
    et remplacer l'ancien fichier d'un objet (vidéo ou photo).
    """
    def post(self, request):
        try:
            # --- 1. Récupération et validation des données de base ---
            
            # Les données sont envoyées en FormData depuis le JavaScript
            object_id = request.POST.get('object_id')
            object_type = request.POST.get('object_type')  # 'video' ou 'photo'
            media_type = request.POST.get('media_type')      # 'cover', 'video_file', 'photo', etc.

            if not object_id or not object_type:
                return JsonResponse({'error': 'ID ou type d\'objet manquant.'}, status=400)

            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Non authentifié.'}, status=401)

            # --- 2. Récupération de l'objet et vérification des permissions ---
            
            ModelClass = Video if object_type == 'video' else Photo
            obj = get_object_or_404(ModelClass, id=object_id)

            # Seul le propriétaire ou un administrateur peut modifier
            if request.user != obj.user and not request.user.is_staff:
                return JsonResponse({'error': 'Accès refusé.'}, status=403)

            # --- 3. Gestion de l'upload d'un nouveau fichier ---
            
            uploaded_file = request.FILES.get('new_file')
            if uploaded_file:
                # Générer un nom de fichier unique et sécurisé
                original_name = uploaded_file.name
                safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', original_name)
                # Utiliser media_type pour organiser les dossiers dans R2 (ex: covers/, videos/)
                unique_filename = f"{media_type}s/{uuid.uuid4().hex[:12]}_{safe_name}"

                # Initialisation du client S3 (compatible R2)
                s3_client = boto3.client(
                    's3',
                    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name='auto'
                )

                # Upload direct du fichier sur R2 avec ACL publique
                s3_client.put_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=unique_filename,
                    Body=uploaded_file.read(),
                    ContentType=uploaded_file.content_type or 'application/octet-stream',
                    ACL='public-read'  # Rendre l'objet public
                )

                # Construction de l'URL publique pour accéder au fichier
                # CORRECTION : Utiliser correctement le domaine CDN
                cdn_domain = getattr(settings, 'R2_CDN_DOMAIN', '').strip()
                if cdn_domain:
                    # Utiliser le domaine CDN personnalisé s'il existe
                    public_root = f"https://{cdn_domain.rstrip('/')}"
                else:
                    # Sinon, utiliser l'endpoint R2 direct (moins performant)
                    public_root = f"{settings.AWS_S3_ENDPOINT_URL.rstrip('/')}/{settings.AWS_STORAGE_BUCKET_NAME}"
                
                new_media_url = f"{public_root}/{unique_filename}"
                
                # Debug
                print(f"CDN Domain: {cdn_domain}")
                print(f"Public Root: {public_root}")
                print(f"Generated URL: {new_media_url}")

                # Mise à jour du champ correspondant dans l'objet
                if object_type == 'video':
                    if media_type == 'cover':
                        obj.cover_image = new_media_url
                    elif media_type == 'video_file':
                        obj.video_file = new_media_url
                elif object_type == 'photo':
                    obj.photo_file = new_media_url
                
                obj.save()

                return JsonResponse({
                    'success': True,
                    'message': f'Le média "{media_type}" a été mis à jour avec succès !',
                    'new_media_url': new_media_url
                })

            # --- 4. Gestion de la mise à jour des métadonnées (si aucun fichier) ---
            
            else:
                # Mise à jour des champs texte pour une vidéo
                if object_type == 'video':
                    title = request.POST.get('title')
                    description = request.POST.get('description')
                    duration_val = request.POST.get('duration')
                    category_id = request.POST.get('category')
                    
                    if title is not None:
                        obj.title = title
                    if description is not None:
                        obj.description = description
                    if duration_val:
                        try:
                            obj.duration = int(duration_val)
                        except ValueError:
                            return JsonResponse({'error': 'La durée doit être un nombre entier.'}, status=400)
                    if category_id:
                        obj.category_id = category_id

                # Mise à jour des champs texte pour une photo
                elif object_type == 'photo':
                    title = request.POST.get('title')
                    description = request.POST.get('description')
                    category_id = request.POST.get('category')
                    
                    if title is not None:
                        obj.title = title
                    if description is not None:
                        obj.description = description
                    if category_id:
                        obj.category_id = category_id

                obj.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Les métadonnées ont été mises à jour avec succès !'
                })

        except json.JSONDecodeError:
            logger.error("JSON invalide dans le corps de la requête ReplaceMediaView.")
            return JsonResponse({'error': 'Requête invalide (JSON mal formé).'}, status=400)
        except Exception as e:
            # Logguer l'erreur complète pour le débogage
            logger.error(f"Erreur inattendue dans ReplaceMediaView: {e}", exc_info=True)
            return JsonResponse({'error': 'Une erreur interne est survenue.'}, status=500)





# =====================================================================
# views app for user 
# =====================================================================
def index(request):
    return render(request, 'user/index.html')