from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.shortcuts import get_object_or_404

from django.contrib.auth.models import User

from .models import *

import datetime

def index(request):
	user = request.user
	return render(request, "index.html", {
		"current_user": user if not user.is_anonymous else None,
	})

def login(request):
	return render(request, "login.html", {
		"superuser": request.user.is_superuser	
	})

def login_post(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(request, 
			username = username, 
			password = password,
	)

	if user is None:
		return render(request, "login.html", {
			"error_message": "Login failed.",
		})
	else:
		django_login(request, user)

	return HttpResponseRedirect(reverse("home"))

def create_user(request):
	current_user = request.user
	if not current_user.is_superuser:
		raise Exception("Only superusers can create useres.")
	username = request.POST['username']
	password = request.POST['password']
	email = request.POST['email']
	
	new_user = User.objects.create_user(username = username,
				password = password,
				email = email)
	new_user.save()
	return HttpResponseRedirect(reverse("login"))

	

def view_resources(request):
	return render(request, "view_resources.html", {
		"resources": Resource.objects.all(),
	})

def create_resource(request):
	name = request.POST['name']
	owner = request.user
	if owner is None or owner.is_anonymous:
		error_msg = "You aren't logged in."
		return render(request, "view_resources.html", {
			"error_message": error_msg,
			"resources": Resource.objects.all(),
		})
	res = Resource(name = name,
		original_owner = owner,
	)
	res.save()

	return HttpResponseRedirect(reverse("view_resources"))

def book_resource(request, resource_id):
	resource = get_object_or_404(Resource, pk=resource_id)
	previous_bookings = Booking.objects \
				.filter(resource=resource_id) \
				.order_by("-start_date").all()

	now = datetime.datetime.now()
	current_booking = Booking.objects \
		.filter(resource = resource_id) \
		.filter(start_date__lte = now) \
		.filter(end_date__gte = now) \
		.all()
	
	#if (len(current_booking > 0)):
		#printf("Schedule collision!")
			
	return render(request, "book_resource.html", {
		"resource": resource,
		"bookings": previous_bookings,
		"current_booking": current_booking[0] if current_booking else None,
	})

def book_resource_post(request, resource_id):
	resource = get_object_or_404(Resource, pk=resource_id)
	user = request.user
	if user is None or user.is_anonymous:
		error_msg = "You aren't logged in."
		return render(request, "book_resource.html", {
			"resource": resource,
			"error_message": error_msg
		})

	start_date = request.POST['start_date']
	end_date = request.POST['end_date']
	
	res = Booking(user = user,
		resource = resource,
		start_date = start_date,
		end_date = end_date,
	)
	res.save()

	return HttpResponseRedirect(reverse("view_resources"))

def feedback(request, resource_id):
	resource = get_object_or_404(Resource, pk=resource_id)
	previous_feedback = Feedback.objects \
				.filter(resource=resource_id) \
				.order_by("-timestamp").all()

	return render(request, "feedback.html", {
		"resource": resource,
		"feedback": previous_feedback,
	})

def feedback_post(request, resource_id):
	resource = get_object_or_404(Resource, pk=resource_id)
	user = request.user
	if user is None or user.is_anonymous:
		error_msg = "You aren't logged in."
		return render(request, "feedback.html", {
			"resource": resource,
			"error_message": error_msg
		})

	content = request.POST['content']
	
	res = Feedback(user = user,
		resource = resource,
		content = content
	)
	res.save()

	return HttpResponseRedirect(reverse("feedback", kwargs = {'resource_id':resource_id}))
