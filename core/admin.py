from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import (
    Category, Video, Photo, SliderItem, Like, Comment,
    SubscriptionPlan, UserSubscription, Payment, Complaint
)
from django.utils import timezone
from datetime import timedelta

# ------------------------
# Category
# ------------------------
@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


# ------------------------
# Video
# ------------------------
@admin.register(Video)
class VideoAdmin(ModelAdmin):
    list_display = ('title', 'category', 'views', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('views', 'created_at')


# ------------------------
# Photo
# ------------------------
@admin.register(Photo)
class PhotoAdmin(ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)


# ------------------------
# Slider
# ------------------------
@admin.register(SliderItem)
class SliderAdmin(ModelAdmin):
    list_display = ('video', 'position', 'created_at')
    list_editable = ('position',)
    readonly_fields = ('created_at',)


# ------------------------
# Likes
# ------------------------
@admin.register(Like)
class LikeAdmin(ModelAdmin):
    list_display = ('user', 'video', 'photo', 'created_at')
    readonly_fields = ('created_at',)


# ------------------------
# Comments
# ------------------------
@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('user', 'video', 'photo', 'text', 'created_at')
    readonly_fields = ('created_at',)


# ------------------------
# Subscription Plan
# ------------------------
@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(ModelAdmin):
    list_display = ('name', 'price', 'duration_days')


# ------------------------
# User Subscription
# ------------------------
@admin.register(UserSubscription)
class UserSubscriptionAdmin(ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active')
    readonly_fields = ('start_date', 'end_date')

    def save_model(self, request, obj, form, change):
        if not obj.start_date:
            obj.start_date = timezone.now()
        if not obj.end_date and obj.plan:
            obj.end_date = obj.start_date + timedelta(days=obj.plan.duration_days)
        super().save_model(request, obj, form, change)

# ------------------------
# Payment
# ------------------------
@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('user', 'plan', 'amount', 'reference', 'status', 'created_at')
    list_filter = ('status', 'plan')
    search_fields = ('reference',)
    readonly_fields = ('created_at',)


# ------------------------
# Complaint
# ------------------------
@admin.register(Complaint)
class ComplaintAdmin(ModelAdmin):
    list_display = ('user', 'subject', 'resolved', 'created_at')
    list_filter = ('resolved', 'created_at')
    search_fields = ('subject', 'message')
    readonly_fields = ('created_at',)
