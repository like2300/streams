# models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Video(models.Model):
    # 🔴 AJOUT: user - seul le propriétaire peut modifier/supprimer
    # ✅ TEMPORAIRE: null=True, blank=True pour la migration
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos', null=True, blank=True)
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # ✅ CHANGEMENT: CharField pour les URLs R2
    video_file = models.CharField(max_length=500, blank=True, null=True)  # URL R2 complète
    cover_image = models.CharField(max_length=500, blank=True, null=True)  # URL R2 complète

    # Metadata
    duration = models.PositiveIntegerField(default=0)  # en secondes
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    views = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    @property
    def video_url(self):
        """Retourne l'URL complète de la vidéo"""
        return self.video_file if self.video_file else ""
    
    @property
    def cover_url(self):
        """Retourne l'URL complète de l'image de couverture"""
        return self.cover_image if self.cover_image else ""


class Photo(models.Model):
    # 🔴 AJOUT: user - seul le propriétaire peut modifier/supprimer
    # ✅ TEMPORAIRE: null=True, blank=True pour la migration
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # ✅ CHANGEMENT: CharField pour l'URL R2
    photo_file = models.CharField(max_length=500, blank=True, null=True)  # URL R2 complète
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    @property
    def image_url(self):
        """Retourne l'URL complète de l'image"""
        return self.photo_file if self.photo_file else ""


class SliderItem(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"Slider: {self.video.title}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ("user", "video"),
            ("user", "photo")
        ]

    def __str__(self):
        if self.video:
            return f"{self.user} likes video: {self.video}"
        return f"{self.user} likes photo: {self.photo}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user}"


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()  # FCFA
    duration_days = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.plan}"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    amount = models.PositiveIntegerField()
    reference = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, default="pending")  # pending | success | failed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} - {self.status}"


class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject