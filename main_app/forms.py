from django import forms
from .models import Media, Review, REVIEW_RATING

class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ['title', 'rating', 'status', 'genre', 'description', 'is_favorite', 'notes']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields['rating'].widget = forms.Select(choices=REVIEW_RATING)