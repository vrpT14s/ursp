from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.shortcuts import get_object_or_404

from django.contrib.auth.models import User, Permission
from django.utils.dateparse import parse_datetime

from .models import *

import datetime
import re

def index(request):
	user = request.user
	return render(request, "index.html", {
		"current_user": user if not user.is_anonymous else None,
		"can_approve": user.is_staff,
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
		raise Exception("Only superusers can create users.")
	print(request.POST)
	username = request.POST['username']
	password = request.POST['password']
	email = request.POST['email']
	is_staff = request.POST.get('is_staff', False)
	if is_staff != False:
		is_staff = True
	
	new_user = User.objects.create_user(username = username,
				password = password,
				email = email,
				is_staff = is_staff)
	new_user.save()
	res_add_perms = request.POST.get('res_add_perms', False)
	book_add_perms = request.POST.get('book_add_perms', False)
	feed_add_perms = request.POST.get('feed_add_perms', False)
	view_unapproved_feedback_perms = request.POST.get('view_unapproved_feedback', False)

	print(Permission.objects.all())
	ar = Permission.objects.get(codename="add_resource")
	ab = Permission.objects.get(codename="add_booking")
	af = Permission.objects.get(codename="add_feedback")
	vf = Permission.objects.get(codename="view_feedback")
	if is_staff or res_add_perms != False:
		new_user.user_permissions.add(ar)
	else:
		new_user.user_permissions.remove(ar)
	if is_staff or book_add_perms != False:
		new_user.user_permissions.add(ab)
	else:
		new_user.user_permissions.remove(ab)
	if is_staff or feed_add_perms != False:
		new_user.user_permissions.add(af)
	else:
		new_user.user_permissions.remove(af)
	if is_staff or view_unapproved_feedback_perms != False:
		new_user.user_permissions.add(vf)
	else:
		new_user.user_permissions.remove(vf)
	if is_staff:
		for codename in [
			"view_resource", "change_resource", "delete_resource",
			"view_booking", "change_booking", "delete_booking",
			"view_feedback", "change_feedback", "delete_feedback",
		]:
			perm = Permission.objects.get(codename=codename)
			new_user.user_permissions.add(perm)
		mod = Moderator(user=new_user)
		mod.save()
	return HttpResponseRedirect(reverse("login"))

	

def view_resources(request):
	return render(request, "view_resources.html", {
		"resources": Resource.objects.all(),
	})

def create_resource(request):
	name = request.POST['name']
	owner = request.user

	resources = Resource.objects.all()
	def error_page(msg):
		return render(request, "view_resources.html", {
			"resources": resources,
			"error_message": msg
		})

	if owner is None or owner.is_anonymous:
		return error_page("You aren't logged in.")
	if not owner.has_perm("booking.add_resource"):
		return error_page("You don't have permission.")

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
		.filter(end_date__gt = now) \
		.all()
	
	#if (len(current_booking > 0)):
		#printf("Schedule collision!")
			
	return render(request, "book_resource.html", {
		"resource": resource,
		"bookings": previous_bookings,
		"current_booking": current_booking[0] if current_booking else None,
	})

def unrealistic_date(date):
	return (date.year >= 2100) or (date.year < 1947)

def book_resource_post(request, resource_id):
	resource = get_object_or_404(Resource, pk=resource_id)
	user = request.user
	def error_page(msg):
		return render(request, "book_resource.html", {
			"resource": resource,
			"error_message": msg
		})

	if user is None or user.is_anonymous:
		return error_page("You aren't logged in.")
	if not user.has_perm("booking.add_booking"):
		return error_page("You don't have permission.")
	start_date = request.POST['start_date']
	end_date = request.POST['end_date']
	sd = parse_datetime(start_date)
	ed = parse_datetime(end_date)

	if unrealistic_date(sd) or unrealistic_date(ed):
		return error_page("Unrealistic dates")
	if (sd > ed):
		return error_page("Start date is after end date.")
	
	from django.db.models import Q
	conflicting = Booking.objects \
		.filter(resource = resource_id) \
		.filter(Q(start_date__gte = start_date) \
		&       Q(start_date__lt = end_date) \
		|       Q(end_date__gte = start_date) \
		&       Q(end_date__lt = end_date)) \
		.all()

	if (len(conflicting) != 0):
		return error_page("Conflicts with a previous booking")
	
	res = Booking(user = user,
		resource = resource,
		start_date = start_date,
		end_date = end_date,
	)
	res.save()

	return HttpResponseRedirect(reverse("view_resources"))

def feedback(request, resource_id):
	resource = get_object_or_404(Resource, pk=resource_id)
	user = request.user
	previous_feedback = Feedback.objects \
				.filter(resource=resource_id) \
				.order_by("-timestamp")
	if not user.has_perm("booking.view_feedback"):
		previous_feedback = previous_feedback \
			.exclude(mod_in_charge=None)
	previous_feedback = previous_feedback.all()

	return render(request, "feedback.html", {
		"resource": resource,
		"feedback": previous_feedback,
		"only_approved": not user.has_perm("booking.view_feedback"),
	})

def feedback_post(request, resource_id):
	resource = get_object_or_404(Resource, pk=resource_id)
	user = request.user

	def error_page(msg):
		previous_feedback = Feedback.objects \
					.filter(resource=resource_id) \
					.order_by("-timestamp")
		if not user.has_perm("booking.view_unapproved_feedback"):
			previous_feedback = previous_feedback \
				.exclude(mod_in_charge=None)
		previous_feedback = previous_feedback.all()
		return render(request, "feedback.html", {
			"resource": resource,
			"feedback": previous_feedback,
			"only_approved": not user.has_perm("booking.view_feedback"),
			"error_message": msg,
		})

	if user is None or user.is_anonymous:
		return error_page("You aren't logged in.")

	if not user.has_perm("booking.add_feedback"):
		return error_page("You don't have permission.")

	content = request.POST['content']
	
	res = Feedback(user = user,
		resource = resource,
		content = content
	)
	res.save()

	return HttpResponseRedirect(reverse("feedback", kwargs = {'resource_id':resource_id}))

def approve_feedback(request):
	unapproved_feedback = Feedback.objects \
				.filter(mod_in_charge=None) \
				.order_by("-timestamp").all()

	return render(request, "approve_feedback.html", {
		"unapproved_feedback": unapproved_feedback,
	})

def approve_feedback_post(request):
	user = request.user

	def error_page(msg):
		unapproved_feedback = Feedback.objects \
				.filter(mod_in_charge=None) \
				.order_by("-timestamp").all()

		return render(request, "approve_feedback.html", {
			"unapproved_feedback": unapproved_feedback,
			"error_message": msg
		})

	print("Help!!!");
	if user is None or user.is_anonymous:
		return error_page("You aren't logged in.")

	print("Help!!!");
	mod_id = Moderator.objects \
		.filter(user=user)\
		.all()
	if len(mod_id) == 0 or not user.has_perm("booking.change_feedback"):
		return error_page("You don't have permission.")
	mod_id = mod_id[0]
	
	print("Help!!!");

	regex = r"approve_(\d+)"
	for key in request.POST.keys():
		print(key)
		comment_id = re.fullmatch(regex, key)
		if comment_id is None:
			continue
		comment_id = int(comment_id.groups()[0])
		print(comment_id)
		comment = get_object_or_404(Feedback, pk=comment_id)
		comment.mod_in_charge = mod_id
		comment.save()

	return HttpResponseRedirect(reverse("approve_feedback"))
