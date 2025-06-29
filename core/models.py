from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Language(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=50)
    flag = models.ImageField(upload_to='flags/', null=True, blank=True)

    def __str__(self):
        return self.name

class WordSet(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    language_from = models.ForeignKey(Language, related_name='sets_from', on_delete=models.CASCADE)
    language_to = models.ForeignKey(Language, related_name='sets_to', on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.language_from} -> {self.language_to})"

class WordCard(models.Model):
    word_set = models.ForeignKey(WordSet, related_name='cards', on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    example = models.TextField(blank=True)
    image = models.ImageField(upload_to='word_images/', null=True, blank=True)
    audio = models.FileField(upload_to='word_audio/', null=True, blank=True)

    def __str__(self):
        return f"{self.word} - {self.translation}"

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(WordCard, on_delete=models.CASCADE)
    repetitions = models.IntegerField(default=0)
    easiness = models.FloatField(default=2.5)
    interval = models.IntegerField(default=1)
    next_review = models.DateField(default=timezone.now)

    def update_spaced_repetition(self, quality):
        """Реализация алгоритма SM-2 для интервальных повторений"""
        if quality < 0 or quality > 5:
            raise ValueError("Quality must be between 0 and 5")
            
        self.easiness = max(1.3, self.easiness + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        
        if quality < 3:
            self.repetitions = 0
            self.interval = 1
        else:
            self.repetitions += 1
            if self.repetitions == 1:
                self.interval = 1
            elif self.repetitions == 2:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.easiness)
        
        self.next_review = timezone.now().date() + timedelta(days=self.interval)
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.card.word} (next: {self.next_review})"

class Test(models.Model):
    TEST_TYPES = [
        ('MC', 'Multiple Choice'),
        ('FB', 'Fill Blank'),
        ('MT', 'Matching'),
    ]
    
    word_set = models.ForeignKey(WordSet, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    test_type = models.CharField(max_length=2, choices=TEST_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_test_type_display()})"

class TestQuestion(models.Model):
    test = models.ForeignKey(Test, related_name='questions', on_delete=models.CASCADE)
    question = models.TextField()
    correct_answer = models.CharField(max_length=100)
    options = models.JSONField(default=list, blank=True)  # For multiple choice

    def __str__(self):
        return f"Q: {self.question[:50]}..."

class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.test.title} ({self.score}%)"