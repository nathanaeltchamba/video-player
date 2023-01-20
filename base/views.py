from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, TemplateView, CreateView
from django.db.models import F, Q, Sum
from .forms import CustomUserCreationForm
from . models import CustomUser, VideoModel


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def format_view_count(view_count):
    if view_count > 999999:
        return '{:,.0f}M'.format(view_count / 1000000)
    elif view_count > 999:
        return '{:,.0f}K'.format(view_count / 1000)
    else:
        return view_count

class SignupView(CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        # make new customeruser
        user = form.save()
        # save customeruser
        user.save()
        return redirect('login')

class ProfileView(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            custom_user = get_object_or_404(CustomUser, username=kwargs['username'])
            videos = VideoModel.objects.filter(creator=custom_user, is_private=False)
            videos = VideoModel.objects.filter(creator=custom_user)
            context['custom_user'] = custom_user
            context['videos'] = videos
            context['user'] = self.request.user
            return context
        except Http404:
            context['error'] = 'User not found'
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if 'error' in context:
            return render(request, 'profile404.html', context)
        return self.render_to_response(context)


class VideoList(ListView):
    model = VideoModel
    template_name = 'list_video.html'
    context_object_name = 'videos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['videos'] = VideoModel.objects.filter(is_private=False)
        return context

class CreateVideo(LoginRequiredMixin, CreateView):
    model = VideoModel
    template_name = 'create_video.html'
    fields = ['title', 'description', 'video_upload', 'thumbnail_upload', 'is_private']

    def form_valid(self, form):
        custom_user, created = CustomUser.objects.get_or_create(username=self.request.user.username)
        form.instance.creator = custom_user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('video-detail', kwargs={'slug': self.object.slug})

class DetailVideo(DetailView):
    model = VideoModel
    template_name = 'detail_video.html'

    def get_object(self, queryset=None):
        return get_object_or_404(VideoModel, slug=self.kwargs.get('slug'))

    def get(self, request, *args, **kwargs):
        video = self.get_object()
        VideoModel.objects.filter(slug=video.slug).update(view_count=F('view_count')+634)
        video.view_count = format_view_count(video.view_count)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        if self.request.user.is_authenticated:
            custom_user = CustomUser.objects.get(username=self.request.user.username)
        else:
            custom_user = None
        video = VideoModel.objects.filter(slug=self.kwargs.get('slug'), creator=custom_user).first()
        if video and custom_user == video.creator:
            context['is_creator'] = True
        else:
            context['is_creator'] = False
        return context



class UpdateVideo(LoginRequiredMixin, UpdateView):
    model = VideoModel
    fields = ['title', 'description']
    template_name = 'update_video.html'

    def form_valid(self, form):
    # Get or create a CustomUser object for the currently logged-in user
        custom_user, created = CustomUser.objects.get_or_create(username=self.request.user.username)
        form.instance.creator = custom_user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('video-detail', kwargs={'slug': self.object.slug})

class DeleteVideo(LoginRequiredMixin, DeleteView):
    model = VideoModel
    template_name = 'delete_video.html'


    def get_success_url(self):
        return reverse('home')

class SearchVideo(View):
    def get(self, request):
        search_query = request.GET.get('search_query')
        keywords = search_query.split(" ")
        videos = VideoModel.objects.none()
        if search_query:
            for keyword in keywords:
                videos |= VideoModel.objects.filter(Q(title__icontains=keyword) | Q(creator__username__icontains=keyword))
            if not videos:
                suggested_videos = VideoModel.objects.all()[:5]
                context = {'message': "No results were found. Here are some suggested videos.", 'suggested_videos': suggested_videos}
            else:
                context = {'videos': videos}
        else:
            videos = VideoModel.objects.all()
            context = {'videos': videos}
        return render(request, 'search_results.html', context)


class VideoDashboard(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    model = VideoModel
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        custom_user = get_object_or_404(CustomUser, username=kwargs['username'])
        context['number_of_videos'] = VideoModel.objects.filter(creator = custom_user).count()
        context['private_videos'] = VideoModel.objects.filter(is_private = True, creator = custom_user).count()
        context['total_views'] = VideoModel.objects.filter(creator=custom_user).aggregate(Sum('view_count'))['view_count__sum']
        context['popular_videos'] = VideoModel.objects.filter(creator=custom_user).order_by('-view_count')[:5]

        return context

    def test_func(self):
        return self.request.user.username == self.kwargs['username']

    def handle_no_permission(self):
        return redirect('home')

