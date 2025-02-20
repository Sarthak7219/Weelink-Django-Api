# from django import forms
# from .models import Profile
# from django.contrib.auth.models import User


# class UpdateUserForm(forms.ModelForm):

#     first_name = forms.CharField(max_length=100,
#                                required=True,
#                                widget=forms.TextInput(attrs={'class': 'form-control'}))
#     username = forms.CharField(max_length=100,
#                                required=True,
#                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    
#     class Meta:
#         model = User
#         fields = ['first_name', 'username']


# class UpdateProfileForm(forms.ModelForm):
#     image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file', 'id' : 'profile_img'}))
#     age = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
#     bio = forms.CharField(
#         max_length=150,
#         widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'cols': 40})
#     )

#     class Meta:
#         model = Profile
#         fields = ['image', 'age', 'bio']
