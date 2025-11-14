from django.core.serializers import serialize
from django.shortcuts import render

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from posts.models import Post, Like, Comment, Image
from posts.serializers import (PostSerializer, CommentSerializer,
                               ImageSerializer, CommentPostSerializer)
from posts.permissions import IsOwnerOrReadOnly

# Create your views here.

class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

# проверяем право доступа, создаем пост,
# проверяем на валидность и  добавлением фотографии

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        else:
            return []

    def create(self, request, *arg, **kwargs):
        serializer = PostSerializer(data =request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(author = self.request.user)

        for image in request.FILES.getlist('image'):
            data = {'image': image, 'post': post.id}
            serializer = ImageSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# размещаем комментарии
class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentPostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_comment(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return post.comments

    def create_comment(self, serializer):
        serializer.save(
            post_id=self.kwargs['post_id'],
            author=self.request.user
        )

# ставим, удаляем лайки
class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = Post.objects.get(id=post_id)
        if not Like.objects.filter(post=post, author=request.user).exists():
            Like.objects.create(post=post, author=request.user)
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, post_id):
        post = Post.objects.get(id=post_id)
        Like.objects.filter(post=post, author=request.user).delete()
        return Response(status=status.HTTP_200_OK)