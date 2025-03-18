from django.conf import settings
from django.db import models

#TODO: add constraints

class Moderator(models.Model):
	#can change this to a OneToOneField
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete = models.CASCADE,
		primary_key = True,
	)
	mod_perms_level = models.IntegerField(null=True)

class Resource(models.Model):
	original_owner = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
	)
	mod_in_charge = models.ForeignKey(
		Moderator,
		on_delete=models.SET_NULL,
		null=True,
	)
	name = models.CharField(max_length=200)


class Booking(models.Model):
	resource = models.ForeignKey(
		Resource,
		on_delete=models.CASCADE,
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
	)

	mod_in_charge = models.ForeignKey(
		Moderator,
		on_delete=models.SET_NULL,
		null=True,
	)
	start_date = models.DateTimeField()
	end_date = models.DateTimeField()
	#add constraint so end >= start
	comment = models.CharField(max_length=200)

class Feedback(models.Model):
	resource = models.ForeignKey(
		Resource,
		on_delete=models.CASCADE,
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
	)
	mod_in_charge = models.ForeignKey(
		Moderator,
		on_delete=models.SET_NULL,
		null=True,
	)
	timestamp = models.DateTimeField(auto_now_add=True)
	rating = models.PositiveIntegerField(null=True) #force to be <= 100?
	content = models.TextField()

