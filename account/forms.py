from django import forms
from account.models import *
from django.contrib.auth.forms import ReadOnlyPasswordHashField


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class ProductForm(forms.ModelForm):
    vendor = forms.ModelChoiceField(queryset = User.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}) )
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    category = forms.ModelChoiceField(queryset = Category.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}) )
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    current_stock = forms.IntegerField(widget=forms.TextInput(attrs={'class':'form-control','min':1}))
    class Meta:
        model = Product
        fields = ['name','category','description','price','image','vendor','current_stock']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("comment","rating")


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone_number')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] and cd['password2'] and cd['password1'] != cd['password2']:
            raise forms.ValidationError('passwords must match')
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'full_name', 'phone_number')

    def clean_password(self):
        return self.initial['password']


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UserRegistrationForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=12,widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('full_name', 'email', 'phone_number')

    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=12,widget=forms.TextInput(attrs={'class': 'form-control'}))
