from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from django.db.models.functions import Lower
from django.contrib.auth.decorators import login_required
from .models import BlogPost
from .forms import BlogPostForm, CommentForm
from profiles.models import UserProfile
from tours.models import Tour


def all_posts(request):

    posts = BlogPost.objects.all()
    query = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'title':
                sortkey = 'lower_title'
                posts = posts.annotate(lower_title=Lower('title'))
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            posts = posts.order_by(sortkey)

        if 'qp' in request.GET:
            query = request.GET['qp']
            if not query:
                messages.error(request, "You didn't enter any search terms!")
                return redirect(reverse('all_posts'))

            queries = Q(title__icontains=query) | Q(content__icontains=query)
            posts = posts.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'posts': posts,
        'search_text': query,
        'current_sorting': current_sorting,
    }

    return render(request, 'blogs/posts.html', context)


def post_detail(request, post_id):
    """ A view to show individual blog post details """

    post = get_object_or_404(BlogPost, pk=post_id)
    tour = Tour.objects.all()
    comments = post.comments.all()
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.blogpost = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'tour': tour,
        'new_comment': new_comment,
        'comment_form': comment_form,
    }

    return render(request, 'blogs/post_detail.html', context)


@login_required
def add_post(request):
    if not request.user.is_superuser:
        messages.error(request,
                       f'Sorry, you are not authorized to do that. If you would like to \
                       add a post to our site please contact us here \
                       { settings.DEFAULT_FROM_EMAIL }.')
        return redirect(reverse('posts'))

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            messages.success(request, f'Successfully added new post \
                             { post.title }!')
            return redirect(reverse('post_detail', args=[post.id]))
        else:
            messages.error(request, 'Failed to add new post. \
                           Please ensure the form is valid.')
    else:
        form = BlogPostForm()

    try:
        profile = UserProfile.objects.get(user=request.user)
        form = BlogPostForm(initial={
            'author': profile.default_full_name,
                })
    except UserProfile.DoesNotExist:
        form = BlogPostForm()

    template = 'blogs/add_post.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_post(request, post_id):
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, you are not authorized to do that')
        return redirect(reverse('posts'))

    post = get_object_or_404(BlogPost, pk=post_id)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid:
            form.save()
            messages.success(request, f'Successfully updated post \
                             { post.title }')
            return redirect(reverse('post_detail', args=[post.id]))
        else:
            messages.error(request, 'Failed to update post. \
                           Check that the form entry is valid')
    else:
        form = BlogPostForm(instance=post)
        messages.info(request, f'You are editing the post {post.title}')

    template = 'blogs/edit_post.html'
    context = {
        'form': form,
        'post': post,
    }

    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, you are not authorized to do that')
        return redirect(reverse('posts'))

    post = get_object_or_404(BlogPost, pk=post_id)
    post.delete()
    messages.success(request, f'Deleted the post { post.title }')
    return redirect(reverse('all_posts'))
