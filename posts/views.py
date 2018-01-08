from urllib.parse import quote_plus
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.contrib import messages

from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from .models import Post
from .forms import PostForm

# Create your views here.


def post_list(request):
    queryset_list = Post.objects.active()
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()
    todays_date = timezone.now().date()

    query = request.GET.get('q')
    if query:
        queryset_list=queryset_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        ).distinct()


    paginator = Paginator(queryset_list, 2)  # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    context = {
            'object_list': queryset,
            'title': 'List',
            'todays_date': todays_date
        }
    return render(request, 'post_list.html', context)




def post_detail(request, slug):
    instance = get_object_or_404(Post, slug=slug)
    if instance.draft or instance.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    share_string = quote_plus(instance.content)
    context = {
        'title': instance.title,
        'instance': instance,
        'share_string': share_string,

    }
    return render(request, 'post_detail.html', context)


def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            messages.success(request, "Successfully cretaed")
            return redirect(instance)

    context = {'form': form}

    return render(request, 'post_form.html', context)



def post_update(request, slug):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(instance=instance)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            updated_post = form.save(commit=False)
            instance.user = request.user
            updated_post.save()
            messages.success(request, "Successfully updated")
            return redirect(updated_post)
    context = {
        'title': instance.title,
        'instance': instance,
        'form': form
    }

    return render(request, 'post_form.html', context)

def post_delete(request, slug):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    messages.success(request, "Successfully deleted")
    return redirect('posts:post_list')

