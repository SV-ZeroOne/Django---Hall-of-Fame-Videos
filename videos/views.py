from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from .models import Hall, Video
from .forms import VideoForm, SearchForm
from django.http import Http404, JsonResponse
from django.forms.utils import ErrorList
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import urllib
import requests

#For function views we use @login_required
#For class based views we use LoginRequiredMixin

# Get youtube API key at https://console.developers.google.com/
YOUTUBE_API_KEY = "someAPIkey"


def home(request):
    recent_halls = Hall.objects.all().order_by('-id')[:3]
    popular_halls = [Hall.objects.get(pk=2),Hall.objects.get(pk=3)]
    return render(request, 'videos/home.html', {'recent_halls' : recent_halls, 'popular_halls' : popular_halls})


@login_required
def dashboard(request):
    halls = Hall.objects.filter(user=request.user)
    return render(request, 'videos/dashboard.html', {'halls':halls})


@login_required
def add_video(request, pk):
    form = VideoForm()
    search_form = SearchForm()
    hall = Hall.objects.get(pk=pk)
    if not hall.user == request.user:
        raise Http404
    if request.method == 'POST':
        # Create video object
        form = VideoForm(request.POST)
        # Does auto validation of form fields
        if form.is_valid():
            video = Video()
            video.hall = hall
            video.url = form.cleaned_data['url']
            parsed_url = urllib.parse.urlparse(video.url)
            video_id = urllib.parse.parse_qs(parsed_url.query).get('v')
            if video_id:
                video.youtube_id = video_id[0]
                response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={ video_id[0] }&key={ YOUTUBE_API_KEY }')
                json = response.json()
                title = json['items'][0]['snippet']['title']
                video.title = title
                video.save()
                return redirect('detail_hall', pk)
            else:
                errors = form._errors.setdefault('url', ErrorList())
                errors.append('Needs to be a valid YouTube URL')

    return render(request, 'videos/add_video.html', {'form':form, 'search_form':search_form, 'hall':hall})


@login_required
def video_search(request):
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        encoded_search_term = urllib.parse.quote(search_form.cleaned_data['search_term'])
        response = requests.get(f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=6&q={ encoded_search_term }&key={ YOUTUBE_API_KEY }')
        return JsonResponse(response.json())
    return JsonResponse({'error':'Not able to validate form'})


class DeleteVideo(LoginRequiredMixin, generic.DeleteView):
    model = Video
    template_name = 'videos/delete_video.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        video = super(DeleteVideo, self).get_object()
        if not video.hall.user == self.request.user:
            raise Http404
        return video


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('dashboard')
    template_name = 'registration/signup.html'

    # Log the user in after signup
    def form_valid(self, form):
       view = super(SignUp, self).form_valid(form)
       username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
       user = authenticate(username=username, password=password)
       login(self.request, user)
       return view


#This is the functional based view way
#def create_hall(request):
#   if request.method == 'POST':
        #get the form data
        #validate form data
        #create hall
        #save hall
#    else:
        #create form for a hall
        #return the template


class CreateHall(LoginRequiredMixin, generic.CreateView):
    model = Hall
    fields = ['title']
    template_name = 'videos/create_hall.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreateHall, self).form_valid(form)
        return redirect('dashboard')


class DetailHall(generic.DetailView):
    model = Hall
    template_name = 'videos/detail_hall.html'


class UpdateHall(LoginRequiredMixin, generic.UpdateView):
    model = Hall
    template_name = 'videos/update_hall.html'
    fields = ['title']
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        hall = super(UpdateHall, self).get_object()
        if not hall.user == self.request.user:
            raise Http404
        return hall


class DeleteHall(LoginRequiredMixin, generic.DeleteView):
    model = Hall
    template_name = 'videos/delete_hall.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        hall = super(DeleteHall, self).get_object()
        if not hall.user == self.request.user:
            raise Http404
        return hall


