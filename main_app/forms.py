from django import forms
from .models import Media, Review, REVIEW_RATING

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['title', 'media_type', 'rating', 'status', 'genre', 'description', 'is_favorite', 'notes', 'difficulty', 'image_url']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your review here...'}),
            'rating': forms.Select(attrs={'class': 'form-control'}, choices=REVIEW_RATING),
        }
        
        labels = {
            'text': 'Review Text',
            'rating': 'Your Rating (optional)',
        }

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields['rating'].widget = forms.Select(choices=REVIEW_RATING)
