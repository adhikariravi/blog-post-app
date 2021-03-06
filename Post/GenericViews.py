# Response Import
import rest_framework
from django.contrib.auth.models import User
from django.http import HttpResponse

# import response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status, generics

# For CSRF Tokens
from django.views.decorators.csrf import csrf_exempt

# Import Generic View
from rest_framework.views import APIView

from Post.models import Post, Comment, Like

# Serializers
from Post.model_serializer import PostSerializer, CommentSerializer, UserSerializer, LikeSerializer
from Post.permissions import IsOwner


class PostList(APIView):

    def get(self, request):
        all_posts = Post.objects.all()
        all_posts_serializer = PostSerializer(all_posts, many=True)
        return Response(all_posts_serializer.data)

    def post(self, request):
        # Save New Post or update
        data = request.data
        post_serializer = PostSerializer(data=data)
        if post_serializer.is_valid():
            post_serializer.save()
            return Response(post_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(post_serializer.errors, status=status.HTTP_404_NOT_FOUND)


class CommentList(APIView):

    def get(self, request, pk):
        # List All Posts
        post = get_object_or_404(Post, pk=pk)
        all_comments = post.comments.all()
        all_comments_serializer = CommentSerializer(all_comments, many=True)
        return Response(all_comments_serializer.data)

    def post(self, request, pk):
        # Save New Post or update
        data = request.data
        comment_serializer = CommentSerializer(data=data)
        if comment_serializer.is_valid():
            comment_serializer.save()
            return Response(comment_serializer.data)
        else:
            return Response(comment_serializer.errors, status=status.HTTP_404_NOT_FOUND)


class PostDetail(APIView):

    def get_object(self, pk):
        post = get_object_or_404(Post, pk=pk)
        return post

    def get(self, request, pk):
        post = self.get_object(pk)
        post_serializer = PostSerializer(post)
        return Response(post_serializer.data)

    def put(self, request, pk):
        data = request.data
        post = self.get_object(pk)
        post_serializer = PostSerializer(post, data=data)
        if post_serializer.is_valid():
            post_serializer.save()
            return Response(post_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, pk):
    #     instance = self.get_object(pk)
    #     instance.archived = True
    #     instance.save()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class ListUser(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminUser, IsOwner)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class CreateDestroyLikeView(APIView):
    permission_classes = (IsOwner, IsAdminUser)
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def post(self, request, pk):
        post_id = pk
        user_id = request.user.id
        like_serializer = LikeSerializer(data={'post': post_id, 'author': user_id})
        if like_serializer.is_valid():
            return Response({'liked': like_serializer.like()})
        else:
            return Response(like_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardView(generics.ListAPIView):
    class PostPagination(PageNumberPagination):
        page_size = 2
        page_size_query_param = 'page_size'
        max_page_size = 100

    pagination_class = PostPagination
    serializer_class = PostSerializer

    def get_queryset(self):
        paginate_type = self.kwargs.get('ctype', None)
        if paginate_type == 'published':
            qs = Post.objects.filter(published=True)
        elif paginate_type == 'unpublished':
            qs = Post.objects.filter(published=False)
        elif paginate_type == 'archived':
            qs = Post.objects.filter(archived=True)
        else:
            qs = Post.objects.none()
        return qs

