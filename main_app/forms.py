from django import forms
from .models import Media, Review

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['title', 'rating', 'status', 'genre', 'description', 'is_favorite', 'notes']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating'] 

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields['rating'].widget = forms.Select(choices=Review.REVIEW_RATING)