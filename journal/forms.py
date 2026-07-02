import ast
import json
from django import forms
from .models import Setup, Finding, StrategyNote

PSYCH_CHOICES = [
    'Calm', 'Confident', 'Hesitant', 'FOMO', 'Revenge urge',
    'Rushed', 'Bored', 'Anxious', 'Moved SL', 'Exited early', 'Stuck to plan',
]


class SetupForm(forms.ModelForm):
    psych_tags = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Setup
        exclude = ['user', 'created_at', 'updated_at', 'sl_distance']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'grade_reason': forms.Textarea(attrs={'rows': 2}),
            'setup_notes': forms.Textarea(attrs={'rows': 3}),
            'improvement_notes': forms.Textarea(attrs={'rows': 2}),
            'psych_note': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_psych_tags(self):
        raw = self.cleaned_data.get('psych_tags')
        tags = []

        if isinstance(raw, list):
            tags = raw
        elif isinstance(raw, str) and raw.strip():
            text = raw.strip()
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    tags = parsed
            except json.JSONDecodeError:
                # Accept Python-style list strings like "['Calm', 'FOMO']".
                try:
                    parsed = ast.literal_eval(text)
                    if isinstance(parsed, list):
                        tags = parsed
                except (SyntaxError, ValueError):
                    tags = []

        allowed = set(PSYCH_CHOICES)
        cleaned = []
        for tag in tags:
            if tag in allowed and tag not in cleaned:
                cleaned.append(tag)
        return cleaned


class FindingForm(forms.ModelForm):
    class Meta:
        model = Finding
        fields = ['setup', 'category', 'text']
        widgets = {'text': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['setup'].queryset = Setup.objects.filter(user=user).order_by('-setup_number')
        self.fields['setup'].required = False
        self.fields['setup'].empty_label = '— General finding (no specific setup) —'


class StrategyNoteForm(forms.ModelForm):
    class Meta:
        model = StrategyNote
        fields = ['content']
        widgets = {'content': forms.Textarea(attrs={'rows': 30})}
