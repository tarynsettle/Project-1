from django import forms
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.html import strip_tags
from django.contrib import messages
from markdown2 import Markdown
import random

from . import util

class NewEntryTitle(forms.Form):
    title = forms.CharField(label="Entry Name", max_length=120)

class NewEntryContent(forms.Form):
    content = forms.CharField(label="",
                              widget=forms.Textarea(attrs={'placeholder': '# Lorem ipsum\n\n**Lorem ipsum** dolor sit amet...', 'style': 'height: 500px'}))

class SearchForm(forms.Form):
    query = forms.CharField(label="",
                            widget=forms.TextInput(attrs={'placeholder': "Search the encyclopedia"}))

class EditContent(forms.Form):
    content = forms.CharField(label="",
                            widget=forms.Textarea(attrs={'style': 'height: 500px'}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def newentry(request):
    if request.method == "POST":
        formT = NewEntryTitle(request.POST)
        formC = NewEntryContent(request.POST)
        if formT.is_valid() and formC.is_valid():
            title = formT.cleaned_data["title"]
            content = formC.cleaned_data["content"]
            if title in util.list_entries():
                messages.error(request, "That entry already exists!")
                return redirect(reverse("encyclopedia:newentry"))
            else:
                util.save_entry(title, content)
                return redirect(f"wiki/{title}")
        else:
            messages.error(request, "Something went wrong. Please try again.")
            return redirect("encyclopedia/newentry.html")
        
    return render(request, "encyclopedia/newentry.html", {
        "formT": NewEntryTitle(),
        "formC": NewEntryContent()
    })


def entry(request, title):
    markdown = Markdown()
    if title in util.list_entries():
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": markdown.convert(util.get_entry(title))
        })
    else:
        return render(request, "encyclopedia/404.html")
    
    
def edit(request, title):
    content = util.get_entry(title)
    if request.method == "POST":
        formE = EditContent(request.POST)
        if formE.is_valid():
            content = formE.cleaned_data["content"]
            util.save_entry(title, content)
        else:
            messages.error(request, "Something went wrong. Please try again.")
        return redirect(f"../../wiki/{title}")
        
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "formE": EditContent(initial={"content": strip_tags(content)})
    })


def randomentry(request):
    title = random.choice(util.list_entries())
    return redirect(f"wiki/{title}")


def search(request):
    if request.method == "POST":
        formQ = SearchForm(request.POST)
        searchhits = 0
        if formQ.is_valid():
            query = formQ.cleaned_data["query"]
            if query in util.list_entries():
                title = query
                return redirect(f"wiki/{title}")
            elif util.search_entries(query) == None:
                searchresults = None
            else:
                searchresults = util.search_entries(query)
                for result in searchresults:
                    searchhits += 1
            
        return render(request, "encyclopedia/search.html", {
                    "searchresults": searchresults,
                    "query": query,
                    "searchhits": searchhits
        })