from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, TemplateView, CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.urls import reverse
from django.db.models import F, Q, Sum
from django.contrib import messages
from django.views import View
from django.core.files.storage import default_storage
from .forms import CustomUserCreationForm, UpdateProfileForm
from . models import User, VideoModel, CustomProfile
import subprocess
import os


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def convert_to_mp4(input_file):
    input_extension = input_file.name.split('.')[-1]
    if input_extension != 'mp4':
        # will have to convert to a different save when using aws bucket
        output_file = 'uploads/videos/' + input_file.name.split('.')[0] + '.mp4'
        subprocess.run(['ffmpeg', '-i', input_file.temporary_file_path(), '-vf', 'scale=1920:-2', '-b:v', '800k', output_file])
        with open(output_file, 'rb') as f:
            default_storage.save(output_file, f)
        return output_file
    else:
        return input_file.name


def generate_thumbnail(input_file):
    output_file = 'uploads/thumbnails/' + os.path.splitext(os.path.basename(input_file))[0] + '.jpg'
    subprocess.run(['ffmpeg', '-ss', '1.5', '-i', input_file, '-vframes', '1', '-vf', 'scale=1920:-2', output_file])
    with open(output_file, 'rb') as f:
        default_storage.save(output_file, f)
    return output_file


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
        messages.success(self.request, 'Your account was created successfully')
        return redirect('login')


class ProfileView(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            custom_user = get_object_or_404(User, username=kwargs['username'])
            videos = VideoModel.objects.filter(creator=custom_user, is_private=False)
            if videos.exists():
                context['videos'] = videos
            else:
                context['videos'] = None
            
            recent_upload = VideoModel.objects.filter(creator=custom_user, is_private=False).last()
            if recent_upload:
                context['recent_upload'] = recent_upload
            else:
                context['recent_upload'] = None

            most_popular = VideoModel.objects.filter(creator=custom_user).order_by('-view_count')
            if most_popular.exists():
                most_popular = most_popular[:3]
            else:
                most_popular = None
            context['most_popular'] = most_popular
            context['custom_user'] = custom_user
            context['user'] = self.request.user
            if self.request.user.is_authenticated and self.request.user.username == custom_user.username:
                context['is_owner'] = True
            if not videos:
                context['has_no_videos'] = True 
            return context
        except Http404:
            context['error'] = 'User not found'
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if 'error' in context:
            return render(request, 'profile404.html', context)
        return self.render_to_response(context)


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = CustomProfile
    form_class = UpdateProfileForm
    template_name = 'profile_update.html'

    def get_object(self, queryset=None):
        return User.objects.get(username=self.kwargs['username'])

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.object.username})

        
class VideoList(ListView):
    model = VideoModel
    template_name = 'list_video.html'
    context_object_name = 'videos'
    ordering = ['uploaded_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['videos'] = VideoModel.objects.filter(is_private=False)
        return context


class CreateVideo(LoginRequiredMixin, CreateView):
    model = VideoModel
    template_name = 'create_video.html'
    fields = ['title', 'description', 'video_upload', 'is_private']

    def form_valid(self, form):
        video_upload = form.cleaned_data.get("video_upload")
        self.object = form.save(commit=False)
        self.object.creator = self.request.user
        self.object.video_upload = convert_to_mp4(video_upload)
        self.object.thumbnail_upload = generate_thumbnail(self.object.video_upload.path)
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('video-detail', kwargs={'slug': self.object.slug})


class UpdateVideo(LoginRequiredMixin, UpdateView):
    model = VideoModel
    fields = ['title', 'description']
    template_name = 'update_video.html'

    def form_valid(self, form):
        custom_user, created = User.objects.get_or_create(username=self.request.user.username)
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
            custom_user = User.objects.get(username=self.request.user.username)
        else:
            custom_user = None
        video = VideoModel.objects.filter(slug=self.kwargs.get('slug'), creator=custom_user).first()
        if video and custom_user == video.creator:
            context['is_creator'] = True
        else:
            context['is_creator'] = False
        return context


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
        users = User.objects.none()
        if search_query:
            for keyword in keywords:
                videos |= VideoModel.objects.filter(Q(title__icontains=keyword) | Q(creator__username__icontains=keyword))
                users |= User.objects.filter(Q(username__icontains=keyword)) 
            if not videos and not users:
                suggested_videos = VideoModel.objects.all()[:5]
                context = {'message': "No results were found. Here are some suggested videos.", 'suggested_videos': suggested_videos}
            else:
                context = {'videos': videos, 'users': users}
        else:
            videos = VideoModel.objects.all()
            context = {'videos': videos}
        return render(request, 'search_results.html', context)


class VideoDashboard(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    model = VideoModel
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        custom_user = get_object_or_404(User, username=kwargs['username'])
        context['videos'] = VideoModel.objects.all()
        context['number_of_videos'] = VideoModel.objects.filter(creator = custom_user).count()
        context['private_videos'] = VideoModel.objects.filter(Q(is_private = True) | Q(is_private=None), creator = custom_user).count()
        context['total_views'] = VideoModel.objects.filter(creator=custom_user).aggregate(Sum('view_count'))['view_count__sum']
        print(context['total_views'])
        context['popular_videos'] = VideoModel.objects.filter(creator=custom_user).order_by('-view_count')[:5]
        if self.request.user.is_authenticated and self.request.user.username == custom_user.username:
            context['is_owner'] = True
        return context


    def test_func(self):
        return self.request.user.username == self.kwargs['username']

    def handle_no_permission(self):
        return redirect('home')
