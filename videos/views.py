from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from .models import Hall, Video
from .forms import VideoForm, SearchForm
from django.http import Http404, JsonResponse
from django.forms.utils import ErrorList
import urllib
import requests


# Get youtube API key at https://console.developers.google.com/
YOUTUBE_API_KEY = "somethinginmygoogleconsole"


def home(request):
    return render(request, 'videos/home.html')


def dashboard(request):
    return render(request, 'videos/dashboard.html')


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


def video_search(request):
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        encoded_search_term = urllib.parse.quote(search_form.cleaned_data['search_term'])
        response = requests.get(f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=6&q={ encoded_search_term }&key={ YOUTUBE_API_KEY }')
        return JsonResponse(response.json())
    return JsonResponse({'error':'Not able to validate form'})


class DeleteVideo(generic.DeleteView):
    model = Video
    template_name = 'videos/delete_video.html'
    success_url = reverse_lazy('dashboard')


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
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


class CreateHall(generic.CreateView):
    model = Hall
    fields = ['title']
    template_name = 'videos/create_hall.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreateHall, self).form_valid(form)
        return redirect('home')


class DetailHall(generic.DetailView):
    model = Hall
    template_name = 'videos/detail_hall.html'


class UpdateHall(generic.UpdateView):
    model = Hall
    template_name = 'videos/update_hall.html'
    fields = ['title']
    success_url = reverse_lazy('dashboard')


class DeleteHall(generic.DeleteView):
    model = Hall
    template_name = 'videos/delete_hall.html'
    success_url = reverse_lazy('dashboard')


