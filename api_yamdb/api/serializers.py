from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import (
    Category, Comment, Genre, Review, Title,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def validate_role(self, value):
        user = self.context.get('request').user
        if not (user.is_admin or user.is_moderator):
            return 'user'
        return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        read_only_fields = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        read_only_fields = ('id',)


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        model = Title

    @staticmethod
    def validate_year(year):
        now_year = datetime.now().year
        if now_year < year:
            raise serializers.ValidationError('Not valid year!')
        return year


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'PATCH':
            return data
        view = self.context.get('view')
        title_id = view.kwargs.get('title_id')
        if Review.objects.filter(
                author=request.user,
                title__id=title_id
        ).exists():
            raise serializers.ValidationError(
                'Ранее вы уже оставляли отзыв на данное произведение!'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username')

    @staticmethod
    def validate_username(username):
        error_names = ('me',)
        if username in error_names:
            raise serializers.ValidationError(
                f"Нельзя использовать имя '{username}'!"
            )
        return username


class JWTUserSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, attrs):
        user = get_object_or_404(
            User,
            username=attrs.get('username')
        )
        if not default_token_generator.check_token(
                user, attrs.get('confirmation_code')
        ):
            raise serializers.ValidationError(self.errors)
        token = AccessToken.for_user(user)
        attrs['token'] = token
        return attrs
