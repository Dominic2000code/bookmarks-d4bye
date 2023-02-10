from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreationForm
from .models import Image
from django.http import JsonResponse
from django.views.decorators.http import require_POST

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
    context = {'section': 'images', 'image': image}
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
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})
