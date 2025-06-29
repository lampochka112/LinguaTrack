from rest_framework import serializers
from core.models import (
    Language, WordSet, WordCard, 
    UserProgress, Test, TestQuestion, TestResult
)
from django.contrib.auth.models import User

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

class WordCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordCard
        fields = '__all__'

class WordSetSerializer(serializers.ModelSerializer):
    cards = WordCardSerializer(many=True, read_only=True)
    language_from = LanguageSerializer(read_only=True)
    language_to = LanguageSerializer(read_only=True)
    
    class Meta:
        model = WordSet
        fields = '__all__'

class UserProgressSerializer(serializers.ModelSerializer):
    card = WordCardSerializer(read_only=True)
    
    class Meta:
        model = UserProgress
        fields = '__all__'

class TestQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestQuestion
        fields = '__all__'

class TestSerializer(serializers.ModelSerializer):
    questions = TestQuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Test
        fields = '__all__'

class TestResultSerializer(serializers.ModelSerializer):
    test = TestSerializer(read_only=True)
    
    class Meta:
        model = TestResult
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user