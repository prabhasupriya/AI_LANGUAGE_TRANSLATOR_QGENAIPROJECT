
import requests
import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import TranslationHistory


# Supported languages
SUPPORTED_LANGUAGES = [
    {'code': 'en', 'name': 'English'},
    {'code': 'te', 'name': 'Telugu (తెలుగు)'},
    {'code': 'hi', 'name': 'Hindi (हिन्दी)'},
    {'code': 'ta', 'name': 'Tamil (தமிழ்)'},
    {'code': 'kn', 'name': 'Kannada (ಕನ್ನಡ)'},
    {'code': 'mr', 'name': 'Marathi (मराठी)'},
    {'code': 'ml', 'name': 'Malayalam (മലയാളം)'},
    {'code': 'bn', 'name': 'Bengali (বাংলা)'},
    {'code': 'gu', 'name': 'Gujarati (ગુજરાતી)'},
    {'code': 'pa', 'name': 'Punjabi (ਪੰਜਾਬੀ)'},
    {'code': 'or', 'name': 'Odia (ଓଡ଼ିଆ)'},
    {'code': 'ur', 'name': 'Urdu (اردو)'},
    {'code': 'as', 'name': 'Assamese (অসমীয়া)'},
    {'code': 'ne', 'name': 'Nepali (नेपाली)'},
    {'code': 'sa', 'name': 'Sanskrit (संस्कृतम्)'},
    {'code': 'es', 'name': 'Spanish (Español)'},
    {'code': 'fr', 'name': 'French (Français)'},
    {'code': 'de', 'name': 'German (Deutsch)'},
    {'code': 'ja', 'name': 'Japanese (日本語)'},
    {'code': 'zh', 'name': 'Chinese (中文)'},
    {'code': 'ar', 'name': 'Arabic (العربية)'}
]


# Home page
def home(request):

    # Fetch the latest 5 translation history records
    history = TranslationHistory.objects.all().order_by('-created_at')[:5]

    context = {
        'languages': SUPPORTED_LANGUAGES,
        'history': history
    }

    return render(request, 'translator/index.html', context)


# Translation API
@csrf_exempt
def django_translate(request):

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method. Use POST.'
        }, status=405)

    try:
        # Read incoming JSON data
        data = json.loads(request.body)

        text = data.get('text', '').strip()
        source_lang = data.get('source_lang', 'Auto-Detect')
        target_lang = data.get('target_lang', 'English')

        # Validate input
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Text to translate cannot be empty.'
            }, status=400)

        # Flask microservice URL
        flask_url = "http://127.0.0.1:5000/translate"

        # Forward request to Flask
        response = requests.post(
            flask_url,
            json={
                'text': text,
                'source_lang': source_lang,
                'target_lang': target_lang
            },
            timeout=30
        )

        flask_data = response.json()

        # Check Flask response
        if response.status_code == 200:

            translated_text = flask_data.get('translated_text', '')

            # Save translation in Django database
            TranslationHistory.objects.create(
                original_text=text,
                translated_text=translated_text,
                source_language=source_lang,
                target_language=target_lang
            )

            return JsonResponse({
                'success': True,
                'translated_text': translated_text,
                'source_lang': source_lang,
                'target_lang': target_lang
            })

        else:
            return JsonResponse({
                'success': False,
                'error': flask_data.get(
                    'error',
                    'Translation failed.'
                )
            }, status=response.status_code)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON request.'
        }, status=400)

    except requests.exceptions.Timeout:
        return JsonResponse({
            'success': False,
            'error': 'Flask translation service timed out.'
        }, status=504)

    except requests.exceptions.ConnectionError:
        return JsonResponse({
            'success': False,
            'error': 'Flask microservice engine is offline.'
        }, status=503)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)
