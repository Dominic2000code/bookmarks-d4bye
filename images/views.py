from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreationForm
from .models import Image
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from actions.utils import create_action
import redis
from django.conf import settings

# connect to redis
r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)
# Create your views here.


@login_required
def image_create(request):
    template_name = 'images/image/create.html'
    if request.method == 'POST':
        # form is sent
        form = ImageCreationForm(data=request.POST)
        if form.is_valid():
            # form data is valid
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            # assign current user to the item
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)
            messages.success(request, 'Image added successfully')
            # redirect to new created item detail view
            return redirect(new_image.get_absolute_url())
    else:
        # build form with data provided by the bookmarklet via get
        form = ImageCreationForm(data=request.GET)
    context = {'section': 'images', 'form': form}
    return render(request, template_name, context)


def image_detail(request, id, slug):
    template_name = 'images/image/detail.html'
    image = get_object_or_404(Image, id=id, slug=slug)
    total_views = r.incr(f'image:{image.id}:views')
    # increment image ranking by 1
    r.zincrby('image_ranking', 1, image.id)
    context = {'section': 'images', 'image': image, 'total_views': total_views}
    return render(request, template_name, context)


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


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # if page not an integer deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            # If AJAX request and page out of range
            # return an empty page
            return HttpResponse('')
        # If page out of range return last page of results
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(request, 'images/image/list_images.html', {'section': 'images', 'images': images})
    return render(request, 'images/image/list.html', {'section': 'images', 'images': images})


@login_required
def image_ranking(request):
    # get image ranking dictionary
    template_name = 'images/image/ranking.html'
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    # get most viewed images
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    context = {'most_viewed': most_viewed}
    return render(request, template_name, context)
