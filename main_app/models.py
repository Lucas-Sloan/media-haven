from django.db import models

# Create your models here.
class Media(models.Model): 
    MEDIA_TYPE_CHOICES = [ 
        ('movie', 'Movie'), 
        ('tv_show', 'TV Show'), 
        ('anime', 'Anime'), 
        ('game' , 'Video Game'),
    ] 

    STATUS_CHOICES = [ 
        ('f', 'Finished'), 
        ('ip', 'In Progress'), 
        ('p', 'Planning'), 
        ('dr', 'Dropped'), 
    ] 


    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES) 
    title = models.CharField(max_length=255) 
    genre = models.CharField(max_length=100, blank=True) # Filled by API
    description = models.TextField(blank=True) # Filled by API 
    rating = models.IntegerlField(max_digits=3, decimal_places=1) # User's rating 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='plan_to_watch') 
    difficulty = models.CharField(max_length=50) # Could be Easy, Medium, Hard, etc. 
    image_url = models.URLField(blank=True) # Filled by API
    notes = models.TextField(blank=True) # Optional user notes 
    is_favorite = models.BooleanField(default=False) # Mark as favorite
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self): 
        return f'{self.title} ({self.media_type})'