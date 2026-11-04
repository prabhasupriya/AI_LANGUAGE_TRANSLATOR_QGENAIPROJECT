
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
            'error': 'Only POST requests are allowed.'
        }, status=405)

    # Read user input
    try:
        if 'application/json' in (request.content_type or ''):

            if not request.body:
                return JsonResponse({
                    'success': False,
                    'error': 'Request body is empty.'
                }, status=400)

            data = json.loads(request.body.decode('utf-8'))

        else:
            data = request.POST.dict()

    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON request.'
        }, status=400)

    if not isinstance(data, dict):
        return JsonResponse({
            'success': False,
            'error': 'Invalid request data.'
        }, status=400)

    text = str(data.get('text', '')).strip()
    source_lang = data.get('source_lang', 'Auto-Detect')
    target_lang = data.get('target_lang', 'English')

    # Validate input
    if not text:
        return JsonResponse({
            'success': False,
            'error': 'Please enter text to translate.'
        }, status=400)

    # Get Flask service URL
    flask_url = os.getenv('FLASK_API_URL', '').strip()

    if not flask_url:
        logger.error('FLASK_API_URL is not configured.')

        return JsonResponse({
            'success': False,
            'error': 'Flask service URL is not configured.'
        }, status=500)

    # Automatically add the translation endpoint
    flask_url = flask_url.rstrip('/')

    if not flask_url.endswith('/translate'):
        flask_url += '/translate'

    # Send request to Flask microservice
    try:
        response = requests.post(
            flask_url,
            json={
                'text': text,
                'source_lang': source_lang,
                'target_lang': target_lang
            },
            headers={
                'Accept': 'application/json'
            },
            timeout=(10, 60)
        )

    except requests.exceptions.Timeout:
        logger.error('Flask translation request timed out.')

        return JsonResponse({
            'success': False,
            'error': 'Translation service took too long. Please try again.'
        }, status=504)

    except requests.exceptions.ConnectionError:
        logger.exception('Could not connect to Flask service.')

        return JsonResponse({
            'success': False,
            'error': 'Unable to connect to translation service.'
        }, status=503)

    except requests.exceptions.RequestException:
        logger.exception('Flask request failed.')

        return JsonResponse({
            'success': False,
            'error': 'Translation service request failed.'
        }, status=502)

    # Convert Flask response to JSON
    try:
        flask_data = response.json()

    except ValueError:
        logger.error(
            'Flask returned non-JSON response. '
            'Status: %s, Content-Type: %s, Body: %s',
            response.status_code,
            response.headers.get('Content-Type'),
            response.text[:500]
        )

        return JsonResponse({
            'success': False,
            'error': 'Flask returned an invalid response. Check Flask logs.'
        }, status=502)

    if not isinstance(flask_data, dict):
        return JsonResponse({
            'success': False,
            'error': 'Invalid data received from Flask.'
        }, status=502)

    # Check Flask response status
    if response.status_code != 200 or not flask_data.get('success', True):
        logger.error(
            'Flask translation failed: status=%s, response=%s',
            response.status_code,
            flask_data
        )

        return JsonResponse({
            'success': False,
            'error': flask_data.get(
                'error',
                'Translation failed. Please try again.'
            )
        }, status=502)

    # Get translated text
    translated_text = flask_data.get('translated_text', '')

    if not isinstance(translated_text, str) or not translated_text.strip():
        return JsonResponse({
            'success': False,
            'error': 'No translated text received from Flask.'
        }, status=502)

    # Save successful translation to database
    try:
        TranslationHistory.objects.create(
            original_text=text,
            translated_text=translated_text,
            source_language=source_lang,
            target_language=target_lang
        )

    except Exception:
        logger.exception('Could not save translation history.')

        return JsonResponse({
            'success': False,
            'error': 'Translation succeeded, but history could not be saved.'
        }, status=500)

    # Return result to frontend
    return JsonResponse({
        'success': True,
        'translated_text': translated_text,
        'source_lang': source_lang,
        'target_lang': target_lang
    })
