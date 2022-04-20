from django.contrib.auth.models import User
from django.shortcuts import render, redirect 
from .models import Profile, Message
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from .utils import pagination_profiles, search_profiles
# Create your views here.


def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'account')
        else:
            messages.error(request, 'Username or password incorrect!')
    context = {'page': page,}
    return render(request, 'users/login_register.html', context )

def logout_user(request):
    logout(request)
    messages.info(request, 'User sucessfull logout!')
    return redirect('login')

def register_user(request):
    page = 'register'
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'User account created sucessfully!')
            login(request, user)
            return redirect('edit_account')
        else:
            messages.error(request, 'And error has ocurred during registration!')
    context={'page': page, 'form':form}
    return render(request, 'users/login_register.html', context)


def profiles(request):
    profiles, search_query = search_profiles(request)
    custom_range, profiles = pagination_profiles(request, profiles, 6)
    context ={
        'profiles':profiles,'search_query':search_query,
        'custom_range':custom_range,
    }
    return render(request, 'users/profiles.html', context)


def profile(request, pk):
    profile = Profile.objects.get(id=pk)
    
    top_skills = profile.skill_set.exclude(description__exact="")
    other_skills = profile.skill_set.filter(description__exact="")

    context = {
        'top_skills':top_skills,
        'profile':profile,
        'other_skills':other_skills,
        
    }
    return render(request, 'users/profile.html', context)

@login_required(login_url='login')
def account(request):
    profile = request.user.profile
    skills = profile.skill_set.all()
    context = { 'profile': profile, 'skills': skills, }
    return render(request, 'users/account.html', context)

def edit_account(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'User account Updated sucessfully!')
            return redirect('account')
    context={'form':form}
    return render(request, 'users/profile_form.html', context)

@login_required(login_url='login')
def create_skill(request):
    profile = request.user.profile
    form = SkillForm()
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, 'Skill added sucessfully!')
            return redirect('account')
    context={'form':form}
    return render(request, 'users/skill_form.html', context)

@login_required(login_url='login')
def update_skill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=skill)

    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():       
            form.save()
            messages.success(request, 'Skill Updated sucessfully!')
            return redirect('account')
    context={'form':form}
    return render(request, 'users/skill_form.html', context)

@login_required(login_url='login')
def delete_skill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill Removed sucessfully!')
        return redirect('account')
    context={'object':skill}
    return render(request, 'delete_template.html', context)

@login_required(login_url='login')
def inbox(request):
    #A (user) -> B (profile)
    profile = request.user.profile
    #B (profile) -> C (messages)
    messageRequests = profile.messages.all()
    # Where read = False
    unreadCount = messageRequests.filter(is_read=False).count()
    context={ 'messageRequests': messageRequests, 'unreadCount':unreadCount}
    return render(request, 'users/inbox.html', context)

@login_required(login_url='login')
def view_message(request, pk):
    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read == False:
        message.is_read = True
        message.save()
    context = {'message':message}
    return render(request, 'users/message.html', context)

def create_message(request, pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm()

    try:
        sender = request.user.profile
    except:
        sender = None
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():  
            message = form.save(commit=False)     
            message.sender = sender
            message.recipient = recipient
            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()
            messages.success(request, 'Your message was sucessfully sent!')
            return redirect('profile', recipient.id)
    context = { 'recipient':recipient, 'form':form }
    return render(request, 'users/message_form.html', context)