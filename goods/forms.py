from django import forms
from .models import Tag, Product


class ProductFilterForm(forms.Form):
    firm = forms.MultipleChoiceField(choices=[], required=False)  # Поле для множественного выбора фирм
    size = forms.MultipleChoiceField(choices=[], required=False)
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        firms = kwargs.pop("firms", [])
        sizes = kwargs.pop("sizes", [])
        super().__init__(*args, **kwargs)
        self.fields["firm"].choices = [(firm, firm) for firm in firms]
        self.fields["size"].choices = [(size, size) for size in sizes]

    def clean_firm(self):
        firms = self.cleaned_data.get("firm", [])
        # Объединяем выбранные фирмы в строку с запятыми
        return ",".join(firms) if firms else ""
