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
        fields = ['title', 'description', 'image_file', 'category']
        
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
            'image_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
