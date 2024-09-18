from django.shortcuts import render, get_object_or_404, redirect
from .models import Media, Review
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
            return redirect('media_index')
    else:
        form = MediaForm()
    return render(request, 'add_edit_media.html', {'form': form, 'media_type': media_type})

# Edit Existing Media
def edit_media(request, id):
    media = get_object_or_404(Media, id=id)
    if request.method == 'POST':
        form = MediaForm(request.POST, instance=media)
        if form.is_valid():
            form.save()
            return redirect('media_index')
    else:
        form = MediaForm(instance=media)
    return render(request, 'add_edit_media.html', {'form': form, 'media': media})

# View Media Details
def view_media(request, id):
    media = get_object_or_404(Media, id=id)
    reviews = Review.objects.filter(media=media)
    return render(request, 'media_details.html', {'media': media, 'reviews': reviews})

# List Favorites
def favorites(request):
    favorite_list = Media.objects.filter(is_favorite=True)
    return render(request, 'favorites.html', {'favorite_list': favorite_list})

# View Media Reviews
def media_reviews(request, id):
    media = get_object_or_404(Media, id=id)
    reviews = Review.objects.filter(media=media)
    return render(request, 'media_reviews.html', {'media': media, 'reviews': reviews})

# Add a Review to Media
def add_review(request, id):
    media = get_object_or_404(Media, id=id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.media = media
            review.save()
            return redirect('media_reviews', id=id)
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form, 'media': media})

# Delete a Review
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        review.delete()
        return redirect('media_reviews', id=id)
    return render(request, 'confirm_delete.html', {'review': review})
