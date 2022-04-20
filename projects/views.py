from types import MethodType
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from projects.models import Project, Tag
from .utils import pagination_projects, search_projects
from users.views import profile
from .forms import ProjectForm, ReviewForm
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


# Create your views here.
def projects(request):
    projects = Project.objects.all()
    projects, search_query = search_projects(request)
    custom_range, projects = pagination_projects(request, projects, 3)

    context={    
        'projects': projects,
        'search_query':search_query,
        'custom_range': custom_range,
    }
    return render(request, 'projects/projects.html', context)

def project(request, pk):
    
    projectObj = Project.objects.get(id=pk)
    tags = projectObj.tags.all()
    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        review = form.save(commit=False)
        review.project = projectObj
        review.owner = request.user.profile
        review.save()
        #Update project vote count
        projectObj.getVoteCount() 
        messages.success(request, 'Your review was sucessfully submitted!')
        return redirect('project', pk=projectObj.id)

    context = {'project' : projectObj, 'tags' : tags, 'form' : form}
    return render(request, 'projects/project.html', context)

@login_required(login_url='login')
def create_project(request):
    profile = request.user.profile
    form = ProjectForm()
    if request.method == 'POST':
            form = ProjectForm(request.POST, request.FILES)
            if form.is_valid():
                project = form.save(commit=False)
                project.owner = profile
                project.save()
                return redirect('account')
    context = {'form': form}
    return render(request, 'projects/project_form.html', context)

@login_required(login_url='login')
def update_project(request, pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    form = ProjectForm(instance=project)

    if request.method == 'POST':
            form = ProjectForm(request.POST, request.FILES, instance=project)
            if form.is_valid():
                form.save()
                return redirect('account')
    context = {'form': form}
    return render(request, 'projects/project_form.html', context)

@login_required(login_url='login')   
def delete_template(request, pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)

    if request.method == 'POST':
        project.delete()
        return redirect('projects')
    context = {
        'object': project
    }
    return render(request, 'delete_template.html', context)