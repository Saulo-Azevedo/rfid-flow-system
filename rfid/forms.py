from django import forms
from .models import Botijao

class NovaLeituraForm(forms.Form):
    """Formulário para registrar nova leitura manual"""
    
    tag_rfid = forms.CharField(
        label='Tag RFID',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: E200000000000001',
            'autofocus': True
        }),
        help_text='Tag RFID do botijão'
    )
    
    numero_serie = forms.CharField(
        label='Número de Série',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Deixe em branco para gerar automaticamente'
        }),
        help_text='Número de série do botijão (gerado automaticamente se não informado)'
    )
    
    operador = forms.CharField(
        label='Operador',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome do colaborador'
        })
    )
    
    localizacao = forms.CharField(
        label='Localização',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Depósito A, Portaria, etc.'
        }),
        help_text='Local onde a leitura foi realizada'
    )
    
    observacao = forms.CharField(
        label='Observação',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Informações adicionais sobre esta leitura...'
        })
    )


class FiltroRelatorioForm(forms.Form):
    """Formulário para filtrar relatórios"""
    
    status = forms.ChoiceField(
        label='Status',
        choices=[('', 'Todos')] + Botijao.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    data_inicio = forms.DateField(
        label='Data Início',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    data_fim = forms.DateField(
        label='Data Fim',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )