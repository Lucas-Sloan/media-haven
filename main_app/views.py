from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Media, Review, MEDIA_TYPE_CHOICES, DIFFICULTY_CHOICES
from .forms import MediaForm, ReviewForm

# Landing page view
class Home(LoginView):
    template_name = 'home.html'

# Dashboard view
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recently_added'] = Media.objects.order_by('-created_at')[:10]
        context['favorites'] = Media.objects.filter(is_favorite=True)
        return context

# Media Index (List all media)
class MediaListView(ListView):
    model = Media
    template_name = 'media/media_index.html'
    context_object_name = 'media_list'

# Media Filtered by Type (Movies, TV Shows, Anime, Video Games)
class MediaFilteredListView(ListView):
    model = Media
    template_name = 'media/media_index.html'
    context_object_name = 'media_list'

    def get_queryset(self):
        return Media.objects.filter(media_type=self.kwargs['media_type'])

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
            status=self.kwargs['status']
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
        if media_type:
            form.instance.media_type = media_type
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media_type'] = self.kwargs.get('media_type')
        context['media_type_choices'] = MEDIA_TYPE_CHOICES
        if self.kwargs.get('media_type') == 'game':
            context['DIFFICULTY_CHOICES'] = DIFFICULTY_CHOICES
        return context

    def get_success_url(self):
        if self.kwargs.get('media_type'):
            return reverse('media_filtered', kwargs={'media_type': self.kwargs.get('media_type')})
        return reverse('media_index')

# Edit Existing Media
class MediaUpdateView(UpdateView):
    model = Media
    form_class = MediaForm
    template_name = 'media/media_form.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media_type_choices'] = MEDIA_TYPE_CHOICES
        return context

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