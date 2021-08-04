# Django
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# local Django
from .models import Image, Images, Post


# Create your forms here

class NewUserForm(
        UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "username", "email", 
            "password1", "password2")

    def save(
            self, 
            commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UpdateProfile(
        forms.ModelForm):
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    gender = forms.ChoiceField(choices=[('0', 'Female'), ('1', 'Male')])
    birthdate = forms.DateTimeField(input_formats=['%d/%m/%Y'])

    class Meta:
        model = User
        fields = (
            'username', 'email', 
            'first_name', 'last_name', 
            'gender', 'birthdate'
        )

    def __init__(
            self, 
            *args, 
            **kwargs): # for access current request user in forms.py
        self.user = kwargs.pop(
            'user', 
            None)
        super(UpdateProfile, self).__init__(*args, **kwargs)

    def clean_email(
            self):
        # print('[+20] self. cleaned_data: ', self.cleaned_data)
        # print('[+] self.user: ', self.user)
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        # print(username)
        # print(email)
        # print(User.objects.filter(email=email))
        # print(User.objects.filter(email=email).exclude(username=username))
        # print(list(User.objects.filter(email=email).exclude(username=username)))
        # print(list(User.objects.filter(email=email).exclude(username=username))[0].username)
        # print(type(list(User.objects.filter(email=email).exclude(username=username))[0].username))

        # print(User.objects.filter(email=email).exclude(username=username).count())
        # print(bool(email and User.objects.filter(email=email).exclude(username=username).count()))

        email_of_existed_user = False
        for user_iter in list(User.objects.filter(email=email).exclude(username=username)):
            # print("user_iter.username: ", user_iter.username)
            # print("len(user_iter.username): ", len(user_iter.username))
            # print("type(self.user): ", type(self.user.username))
            # print("len(self.user): ", len(self.user.username))
            # print("self.user: ", self.user.username)
            if user_iter.username != self.user.username:
                email_of_existed_user = True

        # if email and User.objects.filter(email=email).exclude(username=username).count():
        if (email and 
            email_of_existed_user):
            raise forms.ValidationError('This email address is already in use. Please supply a different email address.')
        return email

    def save(
            self, 
            commit=True):
        user = super(UpdateProfile, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user

# ===== FROM OFFICIAL =====
class UploadFileForm(
        forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

# If want to upload multiple files
class FileFieldForm(
        forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
# =========================

# class ImageForm(forms.ModelForm):
#     """Form for the image model"""
#     class Meta:
#         model = Image
#         fields = ('title', 'image')

class PostForm(
        forms.ModelForm):
    title = forms.CharField(max_length=128)
    body = forms.CharField(
        max_length=245, 
        label="Item Description.")

    class Meta:
        model = Post
        fields = (
            'title', 
            'body', )

class ImageForm(
        forms.ModelForm):
    #image = forms.ImageField(label='Image')
    image = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}), 
        label='Image')

    class Meta:
        model = Images
        fields = ('image', )

class ImageTrimForm(
        forms.ModelForm):
    image = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}), 
        label='Image')
    left = forms.FloatField(
        required=True, 
        widget=forms.NumberInput(attrs={'id': 'form', 'step': "0.01"}))
    top = forms.FloatField(
        required=True, 
        widget=forms.NumberInput(attrs={'id': 'form', 'step': "0.01"}))
    right = forms.FloatField(
        required=True, 
        widget=forms.NumberInput(attrs={'id': 'form', 'step': "0.01"}))
    bottom = forms.FloatField(
        required=True, 
        widget=forms.NumberInput(attrs={'id': 'form', 'step': "0.01"}))

    class Meta:
        model = Images
        fields = (
            'image', 'left', 
            'top', 'right', 'bottom', 
        )

class ImageFrameForm(
        forms.ModelForm):
    image = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}), 
        label='Image')
    padding = forms.IntegerField(required=True)
    COLOR_CHOICES = [
        ("red", "red"),
        ("green", "green"),
        ("blue", "blue"),
        ("yellow", "yellow"),
    ]
    color = forms.ChoiceField(choices=COLOR_CHOICES)

    class Meta:
        model = Images
        fields = (
            'image', 
            'padding', 
            'color', 
        )

class ImageRemoveBackgroundForm(
        forms.ModelForm):
    image = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}), 
        label='Image')
    blur = forms.IntegerField(initial=21)
    canny_thresh_1 = forms.IntegerField(initial=10)
    canny_thresh_2 = forms.IntegerField(initial=200)
    mask_dilate_iter = forms.IntegerField(initial=10)
    mask_erode_iter = forms.IntegerField(initial=10)
    mask_color_b = forms.FloatField(
        initial=1.0, 
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    mask_color_g = forms.FloatField(
        initial=1.0, 
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    mask_color_r = forms.FloatField(
        initial=1.0, 
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    class Meta:
        model = Images
        fields = (
            'image', 'blur', 
            'canny_thresh_1', 'canny_thresh_2', 
            'mask_dilate_iter', 'mask_erode_iter', 
            'mask_color_b', 'mask_color_g', 'mask_color_r'
        )
