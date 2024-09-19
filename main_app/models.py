from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

MEDIA_TYPE_CHOICES = [
    ('movie', 'Movie'),
    ('tv_show', 'TV Show'),
    ('anime', 'Anime'),
    ('game', 'Video Game'),
]

STATUS_CHOICES = [
    ('f', 'Finished'),
    ('ip', 'In Progress'),
    ('p', 'Planning'),
    ('dr', 'Dropped'),
]

REVIEW_RATING = [
    ('r', 'Recommended'),
    ('nr', 'Not Recommended'),
    ('otf', 'On The Fence'),
]

class Media(models.Model):
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100, blank=True)  # Filled by API
    description = models.TextField(blank=True)  # Filled by API
    rating = models.IntegerField(validators=[
        MaxValueValidator(5),
        MinValueValidator(0)
    ])  # User's rating
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='p')
    difficulty = models.CharField(max_length=50,blank=True,null=True)  # Could be Easy, Medium, Hard, etc.
    image_url = models.URLField(blank=True)  # Filled by API
    notes = models.TextField(blank=True)  # Optional user notes
    is_favorite = models.BooleanField(default=False)  # Mark as favorite
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} ({self.media_type})'

class Review(models.Model):
    media = models.ForeignKey(Media, related_name='reviews', on_delete=models.CASCADE)  # Link to Media
    text = models.TextField(max_length=1000)
    rating = models.CharField(max_length=3, choices=REVIEW_RATING, blank=True)  # Optional rating
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Review for {self.media.title}'
