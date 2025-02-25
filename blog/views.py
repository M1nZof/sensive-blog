from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from blog.models import Post, Tag


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.tags_amount,
    }


def index(request):
    counted_tag_queryset = Tag.objects.annotate(tags_amount=Count('id'))

    most_popular_posts = Post.objects.popular().fetch_with_tags(counted_tag_queryset)[:5].fetch_with_comments_count()

    most_fresh_posts = Post.objects.fresh().fetch_with_tags(counted_tag_queryset)[:5].fetch_with_comments_count()

    most_popular_tags = Tag.objects.popular().annotate(tags_amount=Count('posts'))[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts[:5]
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post_queryset = Post.objects.annotate(likes_amount=Count('likes'))
    post = get_object_or_404(post_queryset, slug=slug)
    comments = post.comments.select_related('author').all()
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    related_tags = post.tags.annotate(tags_amount=Count('id')).all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_amount,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular().annotate(tags_amount=Count('id'))[:5]

    counted_tag_queryset = Tag.objects.annotate(tags_amount=Count('id'))

    most_popular_posts = Post.objects.popular().fetch_with_tags(counted_tag_queryset)[:5].fetch_with_comments_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag, title=tag_title)
    counted_tag_queryset = Tag.objects.annotate(tags_amount=Count('id'))

    most_popular_tags = Tag.objects.popular().annotate(tags_amount=Count('id'))[:5]

    most_popular_posts = Post.objects.popular().fetch_with_tags(counted_tag_queryset)[:5].fetch_with_comments_count()

    related_posts = tag.posts.annotate(comments_count=Count('comments')) \
                             .fetch_with_tags(counted_tag_queryset).all()[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
