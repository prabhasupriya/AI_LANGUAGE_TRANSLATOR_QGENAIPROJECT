import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import TranslationHistory

def home(request):
    languages = [
        {'code': 'en', 'name': 'English'},
        {'code': 'te', 'name': 'Telugu (తెలుగు)'},
        {'code': 'hi', 'name': 'Hindi (हिन्दी)'},
        {'code': 'es', 'name': 'Spanish (Español)'},
        {'code': 'fr', 'name': 'French (Français)'},
        {'code': 'de', 'name': 'German (Deutsch)'},
        {'code': 'ja', 'name': 'Japanese (日本語)'},
        {'code': 'zh', 'name': 'Chinese (中文)'},
        {'code': 'ar', 'name': 'Arabic (العربية)'}
    ]
    # Fetch recent history items from the database to show on screen
    history = TranslationHistory.objects.all().order_by('-created_at')[:5]
    return render(request, 'translator/index.html', {'languages': languages, 'history': history})

@csrf_exempt
def django_translate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # 1. Forward request to the running Flask microservice engine
        flask_url = "http://127.0.0.1:5000/translate"
        try:
            response = requests.post(flask_url, json=data, timeout=10)
            flask_data = response.json()
            
            if response.status_code == 200:
                # 2. Core integration step: Save translation data to Django's Database
                TranslationHistory.objects.create(
                    original_text=data.get('text'),
                    translated_text=flask_data.get('translated_text'),
                    source_language=data.get('source_lang'),
                    target_language=data.get('target_lang')
                )
                return JsonResponse({'success': True, 'translated_text': flask_data.get('translated_text')})
            else:
                return JsonResponse({'success': False, 'error': flask_data.get('error')})
                
        except requests.exceptions.ConnectionError:
            return JsonResponse({'success': False, 'error': 'Flask microservice engine is offline.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})