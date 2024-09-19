from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.home, name='home'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('media/add/', views.add_media, name='add_media'),

    path('media/add/<str:media_type>/', views.add_media, name='add_media_by_type'),

    path('media/edit/<int:id>/', views.edit_media, name='edit_media'),

    path('media/', views.media_index, name='media_index'),

    path('media/<int:id>/', views.view_media, name='view_media'),

    path('media/<int:id>/reviews/', views.media_reviews, name='media_reviews'),
    
    path('media/<int:id>/reviews/add/', views.add_review, name='add_review'),

    path('media/<str:media_type>/', views.media_filtered, name='media_filtered'),

    path('media/<str:media_type>/<str:status>/', views.media_filtered_status, name='media_filtered_status'),

    path('favorites/', views.favorites, name='favorites'),

    path('media/<int:id>/reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),

    path('media/<int:id>/delete/', views.delete_media, name='delete_media'), 
] 