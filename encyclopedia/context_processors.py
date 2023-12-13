from .views import SearchForm

def include_search(request):
    return {'formQ': SearchForm()}
