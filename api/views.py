from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth.models import User
from core.models import (
    Language, WordSet, WordCard, 
    UserProgress, Test, TestResult
)
from api.serializers import (
    LanguageSerializer, WordSetSerializer, WordCardSerializer,
    UserProgressSerializer, TestSerializer, TestResultSerializer,
    UserSerializer, UserRegistrationSerializer
)
from django.shortcuts import get_object_or_404

class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

class WordSetViewSet(viewsets.ModelViewSet):
    serializer_class = WordSetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return WordSet.objects.filter(created_by=user) | WordSet.objects.filter(is_public=True)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class WordCardViewSet(viewsets.ModelViewSet):
    serializer_class = WordCardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        wordset_id = self.kwargs.get('wordset_pk')
        return WordCard.objects.filter(word_set_id=wordset_id)
    
    def perform_create(self, serializer):
        wordset = get_object_or_404(WordSet, pk=self.kwargs.get('wordset_pk'))
        serializer.save(word_set=wordset)

class UserProgressViewSet(viewsets.ModelViewSet):
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TestViewSet(viewsets.ModelViewSet):
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        wordset_id = self.kwargs.get('wordset_pk')
        return Test.objects.filter(word_set_id=wordset_id)
    
    def perform_create(self, serializer):
        wordset = get_object_or_404(WordSet, pk=self.kwargs.get('wordset_pk'))
        serializer.save(word_set=wordset)

class TestResultViewSet(viewsets.ModelViewSet):
    serializer_class = TestResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TestResult.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    authentication_classes = []
    permission_classes = []
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ReviewCardsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        today = timezone.now().date()
        cards_to_review = UserProgress.objects.filter(
            user=request.user,
            next_review__lte=today
        ).select_related('card')
        
        serializer = UserProgressSerializer(cards_to_review, many=True)
        return Response(serializer.data)
    
    def post(self, request, card_id):
        progress = get_object_or_404(
            UserProgress, 
            user=request.user, 
            card_id=card_id
        )
        
        quality = request.data.get('quality', 3)
        try:
            quality = int(quality)
            if quality < 0 or quality > 5:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': 'Quality must be integer between 0 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        progress.update_spaced_repetition(quality)
        return Response(
            UserProgressSerializer(progress).data,
            status=status.HTTP_200_OK
        )