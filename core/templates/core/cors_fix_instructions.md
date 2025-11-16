# Instructions pour corriger les erreurs d'upload Cloudflare R2 et CORS

## 1. Installation des dépendances nécessaires

Ajoutez ces packages à votre projet :
```bash
pip install django-cors-headers
```

## 2. Modification du fichier settings.py

Ajoutez ceci à votre settings.py :

```python
# Ajouter corsheaders à INSTALLED_APPS
INSTALLED_APPS = [
    # ... autres apps
    'corsheaders',
    # ... autres apps
]

# Ajouter le middleware CORS
MIDDLEWARE = [
    # ... autres middlewares
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ... autres middlewares
]

# Configuration CORS pour développement
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    # Ajoutez votre URL ngrok ici
]

# Pour développement uniquement - NE PAS UTILISER EN PRODUCTION
CORS_ALLOW_ALL_ORIGINS = True

# Autoriser les en-têtes CSRF
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_CREDENTIALS = True
```

## 3. Correction des vues d'upload dans views.py

Voici la correction pour votre vue de presign :

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import boto3
import uuid
from botocore.config import Config

@csrf_exempt
@require_http_methods(["POST"])
def s3_presign(request):
    try:
        data = json.loads(request.body)
        filename = data.get('filename', '')
        content_type = data.get('contentType', 'video/mp4')
        upload_type = data.get('uploadType', 'videos')
        
        # Générer un nom de fichier unique
        unique_filename = f"{upload_type}/{uuid.uuid4()}_{filename}"
        
        # Configuration du client S3 pour Cloudflare R2
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.CF_R2_ENDPOINT,
            aws_access_key_id=settings.CF_R2_ACCESS_KEY,
            aws_secret_access_key=settings.CF_R2_SECRET_KEY,
            region_name='auto',
            config=Config(signature_version='s3v4')
        )
        
        # Créer un presigned post
        presigned_data = s3_client.generate_presigned_post(
            Bucket=settings.CF_R2_BUCKET,
            Key=unique_filename,
            Fields={
                "Content-Type": content_type
            },
            Conditions=[
                {"Content-Type": content_type},
                ["content-length-range", 0, 2 * 1024 * 1024 * 1024]  # Max 2GB
            ],
            ExpiresIn=3600  # 1 heure
        )
        
        # Réponse avec en-têtes CORS
        response = JsonResponse({
            'url': presigned_data['url'],
            'fields': presigned_data['fields'],
            'method': 'POST',
            'key': unique_filename,
            'public_root': getattr(settings, 'CF_R2_PUBLIC_ROOT', settings.CF_R2_ENDPOINT)
        })
        
        # En-têtes CORS obligatoires
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"

        return response
        
    except Exception as e:
        print(f"Erreur dans s3_presign: {str(e)}")
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
        return response

# Vue pour gérer les OPTIONS (preflight request)
def s3_presign_options(request):
    response = JsonResponse({'status': 'ok'})
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization"
    return response

@csrf_exempt
@require_http_methods(["POST"])
def finalize_upload(request):
    try:
        data = json.loads(request.body)
        # Votre logique de finalisation ici
        # ... votre code actuel ...
        
        response = JsonResponse({
            'success': True,
            'message': 'Upload terminé avec succès',
            'url': '/videos/'  # ou l'URL appropriée
        })
        
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
        
        return response
    except Exception as e:
        print(f"Erreur dans finalize_upload: {str(e)}")
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
        return response
```

## 4. Mise à jour des URLs dans urls.py

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... autres URLs
    path('s3-presign/', views.s3_presign, name='s3_presign'),
    path('s3-presign-options/', views.s3_presign_options, name='s3_presign_options'),
    path('finalize-upload/', views.finalize_upload, name='finalize_upload'),
    # ... autres URLs
]
```

## 5. Configuration Cloudflare R2

Assurez-vous que votre bucket Cloudflare R2 a la configuration CORS suivante :

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "POST", "PUT"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

## 6. Correction du modèle pour les URLs Cloudflare R2

Dans votre modèle (models.py), assurez-vous que les URLs publiques sont correctement formatées :

```python
class Video(models.Model):
    # ... vos champs ...
    
    def get_public_url(self):
        # Assurez-vous que cette URL pointe vers le CDN public de R2
        return f"{settings.CF_R2_PUBLIC_ROOT}/{self.key}"
```

## 7. Redémarrage du serveur

Après avoir fait ces modifications :
1. Exécutez les migrations si nécessaire : `python manage.py makemigrations` et `python manage.py migrate`
2. Redémarrez votre serveur Django : `python manage.py runserver`
3. Testez à nouveau l'upload

## Notes importantes :

- Ne mettez JAMAIS CORS_ALLOW_ALL_ORIGINS = True en production
- Les en-têtes CORS sont critiques pour que les requêtes cross-origin fonctionnent
- La configuration des conditions dans generate_presigned_post doit correspondre à ce que Uppy envoie
- Vérifiez que vos clés Cloudflare R2 ont les permissions nécessaires