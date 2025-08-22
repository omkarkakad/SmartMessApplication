from django import forms
from .models import OrderModel, ActiveMenu

class OrderForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
        required=False
    )
    surname = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter your surname'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        existing_user = kwargs.pop('existing_user', False)
        name_value = kwargs.pop('name_value', '')
        surname_value = kwargs.pop('surname_value', '')
        allow_edit = kwargs.pop('allow_edit', False)
        super().__init__(*args, **kwargs)

        if existing_user:
            self.fields['name'].initial = name_value
            self.fields['surname'].initial = surname_value
            if not allow_edit:
                self.fields['name'].widget.attrs.update({'readonly': 'readonly'})
                self.fields['surname'].widget.attrs.update({'readonly': 'readonly'})

        # Only show menu items from ActiveMenu
        try:
            active_menu = ActiveMenu.objects.latest('updated_at')
            active_items = [item for item in OrderModel.MENU_CHOICES if item[0] in active_menu.menu_items]
        except ActiveMenu.DoesNotExist:
            active_items = OrderModel.MENU_CHOICES  # fallback: show all

        for item in active_items:
            self.fields[item[0]] = forms.IntegerField(
                required=False,
                min_value=0,
                initial=0,
                label=item[1],
                widget=forms.NumberInput(attrs={'placeholder': 'Qty', 'style': 'width:80px;'})
            )

    order_place = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Ex. OPD'}))
    is_paid = forms.ChoiceField(choices=OrderModel.PAID_CHOICES)
