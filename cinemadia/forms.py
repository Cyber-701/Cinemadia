from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Movie, Review, UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Enhanced user registration form"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email manzilingiz'
        })
    )
    first_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ismingiz'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Familiyangiz'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Foydalanuvchi nomi'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Parol'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Parolni tasdiqlang'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            # Create user profile automatically
            UserProfile.objects.create(user=user)
        return user


class ReviewForm(forms.ModelForm):
    """Form for creating movie reviews"""
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10',
                'placeholder': 'Baho (1-10)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Fikringizni yozing...'
            })
        }
        labels = {
            'rating': 'Baho',
            'comment': 'Izoh'
        }


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'birth_date', 'favorite_genres']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'O\'zingiz haqingizda...'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'favorite_genres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sevimli janrlar (vergul bilan ajrating)'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'bio': 'Biografiya',
            'avatar': 'Avatar rasm',
            'birth_date': 'Tug\'ilgan sana',
            'favorite_genres': 'Sevimli janrlar'
        }


class MovieForm(forms.ModelForm):
    """Form for creating/updating movies from admin panel."""

    description = forms.CharField(
        label="Qisqacha mazmun",
        widget=forms.Textarea(attrs={
            'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm transition focus:border-primary focus:ring-2 focus:ring-primary/30',
            'rows': 4,
            'placeholder': 'Film haqida qisqa sharh'
        }),
        required=False
    )

    poster_url = forms.URLField(
        label='Poster URL',
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm transition focus:border-primary focus:ring-2 focus:ring-primary/30',
            'placeholder': 'https://...'
        })
    )

    poster_file = forms.ImageField(
        label='Poster fayli',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm text-slate-200 file:bg-slate-800 file:border-0 file:rounded-lg file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary hover:file:bg-slate-700 transition',
            'accept': 'image/*'
        })
    )

    banner_url = forms.URLField(
        label='Banner URL (Katta premyeralar uchun)',
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm transition focus:border-primary focus:ring-2 focus:ring-primary/30',
            'placeholder': 'https://...'
        })
    )

    banner_file = forms.ImageField(
        label='Banner fayli (16:9 nisbat tavsiya)',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm text-slate-200 file:bg-slate-800 file:border-0 file:rounded-lg file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary hover:file:bg-slate-700 transition',
            'accept': 'image/*'
        })
    )

    trailer_url = forms.URLField(
        label='Treyler URL',
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm transition focus:border-primary focus:ring-2 focus:ring-primary/30',
            'placeholder': 'https://...'
        })
    )

    trailer_file = forms.FileField(
        label='Treyler fayli',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm text-slate-200 file:bg-slate-800 file:border-0 file:rounded-lg file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary hover:file:bg-slate-700 transition',
            'accept': 'video/*'
        })
    )

    video_url = forms.URLField(
        label='Film video URL',
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm transition focus:border-primary focus:ring-2 focus:ring-primary/30',
            'placeholder': 'https://...'
        })
    )

    video_file = forms.FileField(
        label='Film fayli',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm text-slate-200 file:bg-slate-800 file:border-0 file:rounded-lg file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary hover:file:bg-slate-700 transition',
            'accept': 'video/*'
        })
    )

    class Meta:
        model = Movie
        fields = [
            'title', 'category', 'genre', 'rating', 'year', 'status', 'duration',
            'director', 'actors', 'description', 'is_featured',
            'poster_url', 'poster_file',
            'banner_url', 'banner_file',
            'trailer_url', 'trailer_file',
            'video_url', 'video_file',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm transition focus:border-primary focus:ring-2 focus:ring-primary/30',
                'placeholder': 'Masalan, Kod Shadow',
                'autocomplete': 'off',
                'autocapitalize': 'sentences'
            }),
            'category': forms.Select(attrs={'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm transition focus:border-primary focus:ring-2 focus:ring-primary/30'}),
            'genre': forms.TextInput(attrs={'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm transition focus:border-primary focus:ring-2 focus:ring-primary/30', 'placeholder': 'Thriller, Drama'}),
            'rating': forms.NumberInput(attrs={'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm transition focus:border-primary focus:ring-2 focus:ring-primary/30', 'min': 0, 'max': 10, 'step': 0.1}),
            'year': forms.NumberInput(attrs={'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm transition focus:border-primary focus:ring-2 focus:ring-primary/30', 'min': 1900, 'max': 2100, 'step': 1, 'placeholder': '2025'}),
            'status': forms.Select(attrs={'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm transition focus:border-primary focus:ring-2 focus:ring-primary/30'}),
            'duration': forms.TextInput(attrs={'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm transition focus:border-primary focus:ring-2 focus:ring-primary/30', 'placeholder': 'Masalan, 126'}),
            'director': forms.TextInput(attrs={'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm transition focus:border-primary focus:ring-2 focus:ring-primary/30', 'placeholder': 'Rejissyor'}),
            'actors': forms.Textarea(attrs={'class': 'movie-field w-full rounded-xl border border-slate-700/80 bg-slate-900/80 px-4 py-2.5 text-sm transition focus:border-primary focus:ring-2 focus:ring-primary/30', 'rows': 2, 'placeholder': 'Aktyorlarni vergul bilan ajrating'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'rounded border-slate-600'}),
        }
        labels = {
            'title': 'Film nomi',
            'category': 'Kategoriya',
            'genre': 'Janr',
            'rating': 'Reyting',
            'year': 'Premyera yili',
            'status': 'Status',
            'duration': 'Davomiylik (daq)',
            'director': 'Rejissyor',
            'actors': 'Aktyorlar',
            'is_featured': 'Premyera sifatida belgilash',
        }

    def clean(self):
        cleaned = super().clean()

        if not cleaned.get('poster_file') and not cleaned.get('poster_url'):
            raise forms.ValidationError('Poster URL kiritish yoki fayl yuklash zarur.')

        rating = cleaned.get('rating')
        if rating is not None and not 0 <= rating <= 10:
            raise forms.ValidationError('Reyting 0 va 10 oralig‘ida bo‘lishi kerak.')

        # A newly uploaded file wins over the previously stored URL.
        for url_field, file_field in (('trailer_url', 'trailer_file'), ('video_url', 'video_file')):
            if cleaned.get(file_field):
                cleaned[url_field] = ''

        return cleaned
