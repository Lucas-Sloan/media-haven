from django.urls import path
from . import views
from .views import fetch_omdb_data, search_games
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('fetch_omdb/', fetch_omdb_data, name='fetch_omdb'),
    path('search-games/', views.search_games, name='search_games'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('favorites/', views.FavoritesListView.as_view(), name='favorites'),
    path('media/', views.MediaListView.as_view(), name='media_index'),
    path('media/form/', views.MediaFormView.as_view(), name='media_form'),
    path('media/edit/<int:pk>/', views.MediaUpdateView.as_view(), name='edit_media'),
    path('media/add/', views.MediaCreateView.as_view(), name='add_media'),
    path('media/add/<str:media_type>/', views.MediaCreateView.as_view(), name='add_media_by_type'),
    path('media/reviews/edit/<int:pk>/', views.ReviewUpdateView.as_view(), name='edit_review'),
    path('media/<int:pk>/confirm-delete/', views.MediaDeleteView.as_view(), name='confirm_delete_media'),
    path('media/<int:pk>/delete/', views.MediaDeleteView.as_view(), name='delete_media'),
    path('media/<int:pk>/', views.MediaDetailView.as_view(), name='view_media'),
    path('media/<int:pk>/reviews/', views.MediaDetailView.as_view(), name='media_reviews'),
    path('media/<int:pk>/reviews/add/', views.ReviewCreateView.as_view(), name='add_review'),
    path('media/<int:media_id>/reviews/delete/<int:pk>/', views.ReviewDeleteView.as_view(), name='delete_review'),
    path('media/<str:media_type>/', views.MediaFilteredListView.as_view(), name='media_filtered'),
    path('media/<str:media_type>/<str:status>/', views.MediaFilteredStatusView.as_view(), name='media_filtered_status'),

    # Authorization URLs
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
