from django.shortcuts import render, redirect
from django.http import Http404
import random

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    content = util.get_entry(title)

    if content is None:
        all_entries = util.list_entries()
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "entries": all_entries
        })

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": util.markdown_to_html(content)
    })

def search(request):
    if request.method == "POST":
        query = request.POST.get("q", "").strip()
        if not query:
            return redirect("index")

        all_entries = util.list_entries()

        for entry in all_entries:
            if entry.lower() == query.lower():
                return redirect("entry", title=entry)

        matching_entries = [
            entry for entry in all_entries
            if query.lower() in entry.lower()
        ]

        return render(request, "encyclopedia/search.html", {
            "query": query,
            "entries": matching_entries
        })

    return redirect("index")


def create(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        if not title:
            return render(request, "encyclopedia/create.html", {
                "error": "Title is required.",
                "title": title,
                "content": content
            })

        if not content:
            return render(request, "encyclopedia/create.html", {
                "error": "Content is required.",
                "title": title,
                "content": content
            })

        if util.get_entry_exists(title):
            return render(request, "encyclopedia/create.html", {
                "error": f"An encyclopedia entry already exists with the title '{title}'.",
                "title": title,
                "content": content
            })

        util.save_entry(title, content)
        return redirect("entry", title=title)

    return render(request, "encyclopedia/create.html")


def edit(request, title):
    content = util.get_entry(title)

    if content is None:
        all_entries = util.list_entries()
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "entries": all_entries
        })

    if request.method == "POST":
        new_content = request.POST.get("content", "").strip()

        if not new_content:
            return render(request, "encyclopedia/edit.html", {
                "error": "Content is required.",
                "title": title,
                "content": new_content
            })

        util.save_entry(title, new_content)
        return redirect("entry", title=title)

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content
    })


def random_page(request):
    all_entries = util.list_entries()

    if not all_entries:
        return redirect("index")

    random_entry = random.choice(all_entries)
    return redirect("entry", title=random_entry)
