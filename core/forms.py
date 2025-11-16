from django import forms
from .models import Video, Photo, Category



class VideoForm(forms.ModelForm):
    """
    Formulaire pour créer ou modifier une vidéo.
    Il est lié au modèle Video et inclut les champs nécessaires à l'upload.
    """
    class Meta:
        model = Video
        # Liste des champs du modèle qui apparaîtront dans le formulaire
        fields = ['title', 'description', 'video_file', 'cover_image', 'duration', 'category']
        
        # Personnalisation des widgets (champs HTML) pour un meilleur style
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Entrez le titre de la vidéo'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Décrivez votre vidéo...'
            }),
            'video_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Durée en secondes'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class PhotoForm(forms.ModelForm):
    """
    Formulaire pour créer ou modifier une photo.
    Il est lié au modèle Photo.
    """
    class Meta:
        model = Photo
        # Liste des champs du modèle qui apparaîtront dans le formulaire
        fields = ['title', 'description', 'photo_file', 'category']
        
        # Personnalisation des widgets
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le titre de la photo'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Décrivez votre photo...'
            }),
            'photo_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

 

# =====================================================================
# FORMULAIRE DE MODIFICATION DE PHOTO (SANS CHAMP FICHIER)
# =====================================================================

class PhotoEditForm(forms.ModelForm):
    """
    Formulaire pour modifier les métadonnées d'une photo existante.
    N'INCLUT PAS de champ 'image_file' pour éviter les erreurs de validation.
    """
    class Meta:
        model = Photo
        fields = ['title', 'description', 'category']  # Uniquement les métadonnées
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le titre de la photo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Décrivez votre photo...'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }


# =====================================================================
# FORMULAIRE DE MODIFICATION DE VIDÉO (SANS CHAMP FICHIER)
# =====================================================================

class VideoEditForm(forms.ModelForm):
    """
    Formulaire pour modifier les métadonnées d'une vidéo existante.
    N'INCLUT PAS de champ 'video_file' ou 'cover_image' pour éviter les erreurs de validation.
    """
    class Meta:
        model = Video
        fields = ['title', 'description', 'duration', 'category']  # Uniquement les métadonnées
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le titre de la vidéo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Décrivez votre vidéo...'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Durée en secondes'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }