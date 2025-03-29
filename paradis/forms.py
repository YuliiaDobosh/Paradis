from django import forms

class ServiceFilterForm(forms.Form):
    skin_type_choices = [('dry', 'Суха'), ('oily', 'Жирна'), ('combination', 'Комбінована')]
    result_choices = [('hydration', 'Зволоження'), ('cleansing', 'Очищення'), ('brightening', 'Освітлення')]

    skin_type = forms.ChoiceField(
        choices=skin_type_choices,
        widget=forms.Select,
        required=False,
        label="Тип шкіри"
    )
    result = forms.ChoiceField(
        choices=result_choices,
        widget=forms.Select,
        required=False,
        label="Бажаний результат"
    )
    budget = forms.DecimalField(
        min_value=0,
        widget=forms.NumberInput,
        required=False,
        label="Максимальний бюджет"
    )