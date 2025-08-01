from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.shortcuts import get_object_or_404


def get_object(klass, *args, **kwargs):
    try:
        obj = get_object_or_404(klass, *args, **kwargs)
    except klass.DoesNotExist:
        obj = None
    except Http404:
        obj = None
    return obj


def pagination(collection, page, per_page):
    paginator = Paginator(collection, per_page)

    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of books.
        results = paginator.page(paginator.num_pages)

    return results
