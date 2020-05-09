from .models import Post
from django.shortcuts import render
from rest_framework import viewsets
from .serializers import PostSerializer
from rest_framework import permissions

def index(request):
    return render(request, 'index.html')


def dalbitMain(request):
    return render(request, 'dalbitMain.html')


class PostView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
