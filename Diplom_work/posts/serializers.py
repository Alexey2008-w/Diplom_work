from rest_framework import serializers

from posts.models import Post, Like, Comment, Image


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['author', 'text', 'created_at']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image']

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    image = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'text', 'image', 'author', 'created_at', 'comments']

    def to_representation(self, post):
        representation = super().to_representation(post)
        representation['likes_count'] = post.likes.count()
        return representation

class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'created_at']

