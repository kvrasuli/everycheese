import pytest
from pytest_django.asserts import assertContains

from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from everycheese.users.models import User

from ..models import Cheese
from ..views import (
    CheeseCreateView,
    CheeseListView,
    CheeseDetailView,
    CheeseUpdateView,
)
from .factories import CheeseFactory, cheese

pytestmark = pytest.mark.django_db

def test_good_cheese_list_view(rf):
    # Get the request
    request = rf.get(reverse("cheeses:list"))
    # Use the request to get the response
    response = CheeseListView.as_view()(request)
    # test that the response is valid
    assertContains(response,'Cheese List')

def test_good_cheese_detail_view(rf, cheese):
    # Make a request for our new cheese
    url = reverse("cheeses:detail", kwargs={'slug': cheese.slug})
    request = rf.get(url)

    # Use the request to get a response
    callable_obj = CheeseDetailView.as_view()
    response = callable_obj(request, slug=cheese.slug)

    # Test that the response is valid
    assertContains(response, cheese.name)

def test_good_cheese_create_view(rf, admin_user, cheese):
    # Make a request for our new cheese
    request = rf.get(reverse("cheeses:add"))
    # Add an authenticated user
    request.user = admin_user
    # Use the request to get the response
    response = CheeseCreateView.as_view()(request)
    assert response.status_code == 200

def test_good_cheese_list_contains_2_cheeses(rf):
    # let's create a couple cheeses
    cheese1 = CheeseFactory()
    cheese2 = CheeseFactory()
    # create a request and then a response for a list of cheeses
    request = rf.get(reverse("cheeses:list"))
    response = CheeseListView.as_view()(request)
    # assert that the response contains both cheese names in the template
    assertContains(response, cheese1.name)
    assertContains(response, cheese2.name)

def test_detail_contains_cheese_data(rf, cheese):
    # Make a request for our new cheese
    url = reverse("cheeses:detail", kwargs={'slug': cheese.slug})
    request = rf.get(url)
    # use the request to get the response
    callable_obj = CheeseDetailView.as_view()
    response = callable_obj(request, slug=cheese.slug)

    assertContains(response, cheese.name)
    assertContains(response, cheese.get_firmness_display())
    assertContains(response, cheese.country_of_origin.name)

def test_cheese_create_form_valid(rf, admin_user):
    #submit the cheese add form
    form_data = {
        "name": "Paski Sir",
        "description": "A salty hard cheese",
        "firmness": Cheese.Firmness.HARD
    }
    request = rf.post(reverse("cheeses:add"), form_data)
    request.user = admin_user
    response = CheeseCreateView.as_view()(request)
    #Get the cheese based on the game
    cheese = Cheese.objects.get()
    #Test that cheese matches our form
    assert cheese.description == "A salty hard cheese"
    assert cheese.firmness == Cheese.Firmness.HARD
    assert cheese.creator == admin_user

def test_cheese_create_correct_title(rf, admin_user):
    """Page title for CheeseCreateView should be Add Cheese"""
    request = rf.get(reverse('cheeses:add'))
    request.user = admin_user
    response = CheeseCreateView.as_view()(request)
    assertContains(response, 'Add Cheese')

def test_good_cheese_update_view(rf, admin_user, cheese):
    url = reverse("cheeses:update", kwargs={'slug': cheese.slug})
    # make a request for our new cheese
    request = rf.get(url)
    # add an authenticated user
    request.user = admin_user
    # use the request to get the response
    callable_obj = CheeseUpdateView.as_view()
    response = callable_obj(request, slug=cheese.slug)
    # test that the response is valid
    assertContains(response, "Update Cheese")

def test_cheese_update(rf, admin_user, cheese):
    """POST request to CheeseUpdateView updates a cheese and redirects"""
    # Make a request for our new cheese
    form_data = {
        "name": cheese.name,
        "description": "Something new",
        "firmness": cheese.firmness
    }
    url = reverse("cheeses:update", kwargs={'slug': cheese.slug})
    request = rf.post(url, form_data)
    request.user = admin_user
    callable_obj = CheeseUpdateView.as_view()
    response = callable_obj(request, slug=cheese.slug)

    # Check that the cheese has been changed
    cheese.refresh_from_db()
    assert cheese.description == 'Something new'