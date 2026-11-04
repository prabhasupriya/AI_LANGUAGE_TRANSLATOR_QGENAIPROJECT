
import os
import json
import logging
import requests

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import TranslationHistory


logger = logging.getLogger(__name__)


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

    history = TranslationHistory.objects.all().order_by(
        '-created_at'
    )[:5]

    context = {
        'languages': SUPPORTED_LANGUAGES,
        'history': history
    }

    return render(request, 'translator/index.html', context)


# Translation API
@csrf_exempt
def django_translate(request):

    # Accept only POST requests
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method. Use POST.'
        }, status=405)

    try:

        # Read incoming request data
        content_type = request.content_type or ''

        if 'application/json' in content_type:

            if not request.body:
                return JsonResponse({
                    'success': False,
                    'error': 'Request body is empty.'
                }, status=400)

            try:
                data = json.loads(
                    request.body.decode('utf-8')
                )

            except (json.JSONDecodeError, UnicodeDecodeError):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON request.'
                }, status=400)

        else:
            # Support normal HTML form submissions
            data = request.POST.dict()

        # Ensure request data is a dictionary
        if not isinstance(data, dict):
            return JsonResponse({
                'success': False,
                'error': 'Invalid request data.'
            }, status=400)

        # Extract user input
        text = str(data.get('text', '')).strip()

        source_lang = data.get(
            'source_lang', 'Auto-Detect'
        )

        target_lang = data.get(
            'target_lang', 'English'
        )

        # Validate input text
        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Text to translate cannot be empty.'
            }, status=400)

        # Get Flask microservice URL from Render
        flask_url = os.getenv('FLASK_API_URL')

        if not flask_url:
            logger.error('FLASK_API_URL environment variable is missing.')

            return JsonResponse({
                'success': False,
                'error': 'Flask service URL is not configured.'
            }, status=500)

        # Forward request to Flask microservice
        try:

            response = requests.post(
                flask_url,
                json={
                    'text': text,
                    'source_lang': source_lang,
                    'target_lang': target_lang
                },
                timeout=30
            )

        except requests.exceptions.Timeout:

            return JsonResponse({
                'success': False,
                'error': 'Flask translation service timed out.'
            }, status=504)

        except requests.exceptions.ConnectionError:

            return JsonResponse({
                'success': False,
                'error': 'Unable to connect to Flask microservice.'
            }, status=503)

        # Read Flask response safely
        try:
            flask_data = response.json()

        except ValueError:

            logger.error(
                'Flask returned a non-JSON response. Status: %s',
                response.status_code
            )

            return JsonResponse({
                'success': False,
                'error': 'Invalid response received from Flask service.'
            }, status=502)

        # Check Flask response status
        if response.status_code != 200:

            return JsonResponse({
                'success': False,
                'error': flask_data.get(
                    'error',
                    'Translation failed.'
                )
            }, status=502)

        # Get translated text
        translated_text = flask_data.get(
            'translated_text', ''
        )

        if not translated_text:
            return JsonResponse({
                'success': False,
                'error': 'Flask returned an empty translation.'
            }, status=502)

        # Save translation history in Django database
        TranslationHistory.objects.create(
            original_text=text,
            translated_text=translated_text,
            source_language=source_lang,
            target_language=target_lang
        )

        # Send translated result to frontend
        return JsonResponse({
            'success': True,
            'translated_text': translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang
        })

    except Exception:

        logger.exception('Unexpected error in django_translate.')

        return JsonResponse({
            'success': False,
            'error': 'An internal server error occurred.'
        }, status=500)
