from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Media, Review, MEDIA_TYPE_CHOICES
from .forms import MediaForm, ReviewForm

# Landing page view
def home(request):
    return render(request, 'home.html')

# Dashboard view
def dashboard(request):
    # Display recently added media and favorites in the dashboard
    recently_added = Media.objects.order_by('-created_at')[:10]
    favorites = Media.objects.filter(is_favorite=True)
    return render(request, 'dashboard.html', {
        'recently_added': recently_added,
        'favorites': favorites,
    })

# Media Index (List all media)
def media_index(request):
    media_list = Media.objects.all()  # Fetch all media
    return render(request, 'media/media_index.html', {'media_list': media_list})

# Media Filtered by Type (Movies, TV Shows, Anime, Video Games)
def media_filtered(request, media_type):
    media_list = Media.objects.filter(media_type=media_type)
    return render(request, 'media/media_index.html', {'media_list': media_list, 'media_type': media_type})

# Media Filtered by Type and Status (e.g., Watching, Watched, etc.)
def media_filtered_status(request, media_type, status):
    media_list = Media.objects.filter(media_type=media_type, status=status)
    return render(request, 'media/media_index.html', {
        'media_list': media_list,
        'media_type': media_type,
        'status': status,
    })

# Add Media (General or by Type)
def add_media(request, media_type=None):
    if request.method == 'POST':
        form = MediaForm(request.POST)
        if form.is_valid():
            media = form.save(commit=False)
            if media_type:
                media.media_type = media_type
            media.save()
            return redirect('media_filtered', media_type=media.media_type)  # Redirect to filtered view
    else:
        form = MediaForm()

    context = {
        'form': form,
        'media_type': media_type,
        'media_type_choices': MEDIA_TYPE_CHOICES  # Pass media type choices
    }
    return render(request, 'media/media_form.html', context)

# Edit Existing Media
def edit_media(request, id):
    media = get_object_or_404(Media, id=id)
    if request.method == 'POST':
        form = MediaForm(request.POST, instance=media)
        if form.is_valid():
            form.save()
            return redirect('media_filtered', media_type=media.media_type)
    else:
        form = MediaForm(instance=media)

    context = {
        'form': form,
        'media': media,
        'media_type_choices': MEDIA_TYPE_CHOICES  # Pass media type choices
    }
    return render(request, 'media/media_form.html', context)

# Delete Media
def confirm_delete_media(request, id):
    media = get_object_or_404(Media, id=id)
    return render(request, 'media/confirm_delete_media.html', {'media': media})

def delete_media(request, id):
    media = get_object_or_404(Media, id=id)
    if request.method == 'POST':
        media.delete()
        return redirect('media_filtered', media_type=media.media_type)  # Redirect to the filtered media list
    return render(request, 'media/media_index.html', {'media': media})

# View Media Details
def view_media(request, id):
    media = get_object_or_404(Media, id=id)
    reviews = Review.objects.filter(media=media)
    return render(request, 'media/media_detail.html', {'media': media, 'reviews': reviews})

# List Favorites
def favorites(request):
    favorite_list = Media.objects.filter(is_favorite=True)
    return render(request, 'favorites.html', {'favorite_list': favorite_list})

# View Media Reviews
def media_reviews(request, id):

    media = get_object_or_404(Media, id=id)
    reviews = Review.objects.filter(media=media)
    return render(request, 'media/media_detail.html', {'media': media, 'reviews': reviews})

# Add a Review to Media
def add_review(request, id):
  
    media = get_object_or_404(Media, id=id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.media = media
            review.save()
            return redirect('media_reviews', id=id)  # Redirect to the media's reviews
    else:
        form = ReviewForm()

    return render(request, 'review/review_form.html', {'form': form, 'media': media, 'review': None})

# Edit an Existing Review
def edit_review(request, review_id):
 
    review = get_object_or_404(Review, id=review_id)
    media = review.media  # Retrieve the associated media item
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('media_reviews', id=media.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'review/review_form.html', {'form': form, 'media': media, 'review': review})

# Delete a Review
def delete_review(request, id, review_id):
   
    review = get_object_or_404(Review, id=review_id)
    media = review.media
    if request.method == 'POST':
        review.delete()
        return redirect('media_reviews', id=media.id)

    return render(request, 'confirm_delete.html', {'review': review, 'media': media}) 