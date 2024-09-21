from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.conf import settings
from decouple import config
from .models import Media, Review, MEDIA_TYPE_CHOICES, DIFFICULTY_CHOICES
from .forms import MediaForm, ReviewForm
from main_app.utils import fetch_omdb_data, fetch_rawg_game_data
import requests # type: ignore
import logging # type: ignore

# Landing page view
class Home(LoginView):
    template_name = 'home.html'

# Dashboard view
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['recently_added'] = Media.objects.filter(user=user).order_by('-created_at')[:10]
        context['favorites'] = Media.objects.filter(user=user, is_favorite=True)
        return context

# Media Index (List all media)
class MediaListView(ListView):
    model = Media
    template_name = 'media/media_index.html'
    context_object_name = 'media_list'

    def get_queryset(self):
        return Media.objects.filter(user=self.request.user)

# Media Filtered by Type (Movies, TV Shows, Anime, Video Games)
class MediaFilteredListView(ListView):
    model = Media
    template_name = 'media/media_index.html'
    context_object_name = 'media_list'

    def get_queryset(self):
        return Media.objects.filter(media_type=self.kwargs['media_type'], user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media_type'] = self.kwargs['media_type']
        return context

    def get_success_url(self):
        media_type = self.kwargs.get('media_type')
        if media_type:
            return reverse('media_filtered', kwargs={'media_type': media_type})
        return reverse('media_index')

# Media Filtered by Type and Status
class MediaFilteredStatusView(ListView):
    model = Media
    template_name = 'media/media_index.html'
    context_object_name = 'media_list'

    def get_queryset(self):
        return Media.objects.filter(
            media_type=self.kwargs['media_type'],
            status=self.kwargs['status'],
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media_type'] = self.kwargs['media_type']
        context['status'] = self.kwargs['status']
        return context

# Add Media
class MediaCreateView(LoginRequiredMixin, CreateView):
    model = Media
    form_class = MediaForm
    template_name = 'media/media_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        media_type = self.kwargs.get('media_type')
        search_title = self.request.POST.get('title')
        
        # Initialize game_data and media_data
        game_data = None
        media_data = None

        # Fetch game data from RAWG if media_type is 'game'
        if media_type == 'game':
            game_data = fetch_rawg_game_data(search_title)

        if game_data:
    # Populate form fields with data fetched from RAWG
            form.instance.title = game_data.get('title')
            form.instance.genre = game_data.get('genre', '')
            form.instance.description = game_data.get('description_raw') or game_data.get('description', '')
            form.instance.image_url = game_data.get('image_url', '')
        else:
            # Use OMDB API for movies/TV shows
            media_data = fetch_omdb_data(search_title)

            if media_data:
                # Populate form fields with data fetched from OMDB
                form.instance.title = media_data.get('title')
                form.instance.genre = media_data.get('genre', '')
                form.instance.description = media_data.get('description', '')
                form.instance.image_url = media_data.get('image_url', '')

        # Ensure media type is assigned
        if media_type:
            form.instance.media_type = media_type

        # Check if title is set before saving
        if not form.instance.title:
            form.add_error('title', 'Unable to fetch media data. Please check the title and try again.')
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['omdb_api_key'] = settings.OMDB_API_KEY
        context['giantbomb_api_key'] = settings.GIANTBOMB_API_KEY
        context['media_type'] = self.kwargs.get('media_type')
        context['media_type_choices'] = MEDIA_TYPE_CHOICES
        if self.kwargs.get('media_type') == 'game':
            context['DIFFICULTY_CHOICES'] = DIFFICULTY_CHOICES
        return context

    def get_success_url(self):
        if self.kwargs.get('media_type'):
            return reverse('media_filtered', kwargs={'media_type': self.kwargs.get('media_type')})
        return reverse('media_index')
    
# Fetch RAWG Data
def fetch_rawg_data(request):
    query = request.GET.get('query', '')
    api_key = config('RAWG_API_KEY')  # Retrieve the API key from environment variables
    url = f'https://api.rawg.io/api/games'

    params = {
        'key': api_key,
        'page_size': 5,  # Adjust page size as needed
        'search': query,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception if the request fails
        data = response.json()

        if data.get('results'):
            return JsonResponse(data)
        else:
            logging.error(f"RAWG API error: No results found for query '{query}'.")
            return JsonResponse({'error': 'No results found'}, status=404)

    except requests.exceptions.Timeout:
        logging.error('Request to RAWG API timed out.')
        return JsonResponse({'error': 'Request timed out'}, status=504)

    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException occurred: {str(e)}")
        return JsonResponse({'error': 'An error occurred while fetching data from RAWG'}, status=500)


# Edit Existing Media
class MediaUpdateView(LoginRequiredMixin, UpdateView):
    model = Media
    form_class = MediaForm
    template_name = 'media/media_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        media_type = self.kwargs.get('media_type')
        
        # Check if the media type is 'game' and fetch data from GiantBomb
        if media_type == 'game':
            search_title = self.request.POST.get('title')
            game_data = fetch_rawg_game_data(search_title)

            if game_data:
                # Update the media instance with the fetched GiantBomb data
                form.instance.title = game_data.get('title')
                form.instance.genre = game_data.get('genre', '')
                form.instance.description = game_data.get('description', '')
                form.instance.image_url = game_data.get('image_url', '')
        else:
            # Use OMDB API for movies/TV shows
            search_title = self.request.POST.get('title')
            media_data = fetch_omdb_data(search_title)

            if media_data:
                # Update the media instance with the fetched OMDB data
                form.instance.title = media_data.get('title')
                form.instance.genre = media_data.get('genre', '')
                form.instance.description = media_data.get('description', '')
                form.instance.image_url = media_data.get('image_url', '')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['omdb_api_key'] = settings.OMDB_API_KEY
        context['giantbomb_api_key'] = settings.GIANTBOMB_API_KEY  # Add GiantBomb API Key to context
        context['media_type_choices'] = MEDIA_TYPE_CHOICES
        context['media_type'] = self.object.media_type  # Ensure media_type is passed
        if self.object.media_type == 'game':
            context['DIFFICULTY_CHOICES'] = DIFFICULTY_CHOICES
        return context

    def get_success_url(self):
        # After updating, redirect to the media detail view
        return reverse('view_media', kwargs={'pk': self.object.pk})

# Delete Media
class MediaDeleteView(DeleteView):
    model = Media
    template_name = 'media/confirm_delete_media.html'

    def get_success_url(self):
        media_type = self.object.media_type
        if media_type:
            return reverse('media_filtered', kwargs={'media_type': media_type})
        return reverse('media_index')

# View Media Details
class MediaDetailView(DetailView):
    model = Media
    template_name = 'media/media_detail.html'
    context_object_name = 'media'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(media=self.object)
        return context

# List Favorites
class FavoritesListView(ListView):
    model = Media
    template_name = 'favorites.html'
    context_object_name = 'favorite_list'

    def get_queryset(self):
        return Media.objects.filter(is_favorite=True)

# Add Review
class ReviewCreateView(CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'review/review_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media'] = get_object_or_404(Media, id=self.kwargs['pk'])
        context['review'] = None
        return context
    
    def form_valid(self, form):
        review = form.save(commit=False)
        review.media = get_object_or_404(Media, id=self.kwargs['pk'])
        review.user = self.request.user
        review.save()
        return redirect(reverse('view_media', kwargs={'pk': review.media.pk}))
    
    def get_success_url(self):
        return reverse('media_reviews', kwargs={'pk': self.object.media.pk})

# Edit Review
class ReviewUpdateView(UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'review/review_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media'] = self.object.media 
        context['review'] = self.object  
        return context
    
    def get_success_url(self):
        return reverse('media_reviews', kwargs={'pk': self.object.media.pk})

# Delete Review
class ReviewDeleteView(DeleteView):
    model = Review
    template_name = 'review/confirm_delete_review.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media'] = self.object.media  # Ensure 'object' is available
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Retrieve the object
        if 'confirm' in request.POST:
            return super().post(request, *args, **kwargs)  # Proceed with deletion
        return redirect(reverse('media_reviews', kwargs={'pk': self.object.media.pk}))  # Redirect if not confirmed

    def get_success_url(self):
        return reverse('media_reviews', kwargs={'pk': self.object.media.pk})
    
# Custom signup view
class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')  # Redirect to login page after successful signup

# Custom login view (uses built-in Django LoginView)
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
class MediaFormView(View):
    template_name = 'media/media_form.html'

    def fetch_media_data(self, search_title):
        return fetch_omdb_data(search_title)

    def post(self, request, *args, **kwargs):
        search_title = request.POST.get('search_title')
        media_type = request.POST.get('media_type', kwargs.get('media_type', None))
        form = MediaForm(request.POST)

        if search_title:
            media_data = self.fetch_media_data(search_title)

            if media_data:
                form = MediaForm(initial={  # Pre-fill form
                    'title': media_data.get('title', ''),
                    'genre': media_data.get('genre', ''),
                    'description': media_data.get('description', ''),
                    'image_url': media_data.get('image_url', ''),
                    'rating': media_data.get('rating', ''),
                    'status': media_data.get('status', None),
                })
            else:
                return render(request, self.template_name, {
                    'form': form,
                    'error': 'Media not found',
                    'search_title': search_title,
                    'media_type': media_type,
                })
        
        # Validate and save the form
        if form.is_valid():
            form.save()
            return redirect('media_index')

        return render(request, self.template_name, {
            'form': form,
            'media_type': media_type,
        })

    def get(self, request, *args, **kwargs):
        media_type = kwargs.get('media_type', None)
        form = MediaForm()
        return render(request, self.template_name, {
            'form': form,
            'media_type': media_type,
        })

