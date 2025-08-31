from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import F
from .models import Post

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    queryset = Post.objects.filter(status='published').order_by('-created_at')
    paginate_by = 5

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        # Increment view count without causing a new save signal
        Post.objects.filter(pk=post.pk).update(views=F('views') + 1)
        
        # Get related posts based on shared categories
        if post.categories.exists():
            related_posts = Post.objects.filter(
                status='published', 
                categories__in=post.categories.all()
            ).exclude(pk=post.pk).distinct().order_by('-created_at')[:3]
            context['related_posts'] = related_posts
            
        return context

def blog_home(request):
    return render(request, 'blog/home.html')
