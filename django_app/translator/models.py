from django.db import models

class TranslationHistory(models.Model):
    original_text = models.TextField()
    translated_text = models.TextField()
    source_language = models.CharField(max_length=50)
    target_language = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_language} to {self.target_language} ({self.created_at.strftime('%Y-%m-%d')})"