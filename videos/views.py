from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from .models import Hall


# Create your views here.

def home(request):
    return render(request, 'videos/home.html')


def dashboard(request):
    return render(request, 'videos/dashboard.html')


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
