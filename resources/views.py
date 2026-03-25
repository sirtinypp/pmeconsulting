from django.shortcuts import render, get_object_or_404
from .models import Post


def resource_list(request):
    category = request.GET.get('cat', '')
    posts = Post.objects.filter(is_published=True)
    if category:
        posts = posts.filter(category=category)

    diy_posts     = Post.objects.filter(is_published=True, category='DIY').order_by('-published_at')[:6]
    article_posts = Post.objects.filter(is_published=True, category='ART').order_by('-published_at')[:6]
    news_posts    = Post.objects.filter(is_published=True, category='NEWS').order_by('-published_at')[:4]

    return render(request, 'resources/list.html', {
        'posts': posts,
        'diy_posts': diy_posts,
        'article_posts': article_posts,
        'news_posts': news_posts,
        'active_cat': category,
        'categories': Post.Category.choices,
    })


def resource_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    related = Post.objects.filter(
        is_published=True, category=post.category
    ).exclude(pk=post.pk)[:3]

    return render(request, 'resources/detail.html', {
        'post': post,
        'related': related,
    })
