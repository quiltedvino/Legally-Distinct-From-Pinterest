from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from .models import Image
from comments.models import Comment
from comments.forms import CommentForm
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType
from actions.utils import create_action
import redis
from django.conf import settings
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Connect to redis
if settings.USE_REDIS:
    r = redis.Redis(host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB)
else:
    r = False


def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')

    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            # If AJAX request and page out of range
            #  return an empty page.
            return HttpResponse('')
        # If page out of range return last page of results
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(request,
                      'images/image/list_images.html',
                      {'section': 'images', 'images': images})
    return render(request,
                  'images/image/list.html',
                  {'section': 'images', 'images': images})


@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    comments = Comment.objects.filter(target_id=id)
    if r:
        total_views = r.incr(f'image:{image.id}:views')
        r.zincrby('image_ranking', 1, image.id)
    else:
        total_views = None

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            # Set the values of target_id, target_ct, and poster
            form.instance.target_id = id
            form.instance.target_ct = ContentType.objects.get(
                app_label='images', model='image')
            # Assuming the poster is the currently logged-in user
            form.instance.poster = request.user
            form.save()
            create_action(request.user, 'commented on',
                          Image.objects.get(id=id))
            messages.success(
                request, f'Comment posted successfully!')

    form = CommentForm()

    return render(request,
                  'images/image/detail.html',
                  {'section': 'images', 'image': image,
                   'total_views': total_views,
                   'comments': comments,
                   'form': form})


@login_required
def image_create(request):
    if request.method == 'POST':
        # Form has been sent
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)
            messages.success(request, 'Image added successfully')
            return redirect(new_image.get_absolute_url())

    else:
        form = ImageCreateForm(data=request.GET)
    return render(request, 'images/image/create.html',
                  {'section': 'images', 'form': form})


@login_required
def image_ranking(request):
    if r:
        image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
        image_ranking_ids = [int(id) for id in image_ranking]
        most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
        most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    else:
        most_viewed = None
    return render(request,
                  'images/image/ranking.html',
                  {'section': 'images', 'most_viewed': most_viewed})
