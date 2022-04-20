from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from .models import Project, Tag

def search_projects(request):   
    search_query=""  
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')   
    tags = Tag.objects.filter(name__icontains=search_query)
    projects = Project.objects.distinct().filter(   Q(title__icontains=search_query) |
                                                    Q(description__icontains=search_query) |
                                                    Q(owner__name__icontains=search_query) |
                                                    Q(tags__in=tags)
                                                    )
    return projects, search_query

def pagination_projects(request, projects, results):
    page = request.GET.get('page')    
    paginator = Paginator(projects, results)
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        page=1
        projects = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
    
    left_index = (int(page)-4)
    if left_index < 1:
        left_index = 1
    right_index = (int(page)+5)
    if right_index > paginator.num_pages:
        right_index = paginator.num_pages+1
    custom_range = range(left_index, right_index)
    return custom_range, projects