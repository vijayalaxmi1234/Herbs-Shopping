from django import forms
from account.models import *

class ProductForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    category = forms.ModelChoiceField(queryset = Category.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}) )
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    price = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Product
        fields = ['name','category','description','price','image']

