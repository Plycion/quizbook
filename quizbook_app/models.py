import hashlib, sys
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import Http404

class Course(models.Model):
	name        = models.CharField(max_length=100)
	description = models.CharField(max_length=1000)
	create_date = models.DateTimeField(auto_now=True, blank=True)
	pub_date    = models.DateTimeField('date published')
	students    = models.ManyToManyField(User)
	creator     = models.CharField(max_length=200, default='Anonymous')

	def __unicode__(self):
		return self.name

class Quiz(models.Model):
	course        = models.ForeignKey(Course)
	question      = models.CharField(max_length=1000)
	answer        = models.CharField(max_length=2000)
	creator       = models.CharField(max_length=200, default='Anonymous')
	pub_date      = models.DateTimeField('date published')
	modified_date = models.DateTimeField('date modified', auto_now=True)

	def __unicode__(self):
		return unicode(self.course) + " : " + self.question

class Grade(models.Model):
	grade = models.IntegerField(default=0)
	quiz  = models.ForeignKey(Quiz)
	user  = models.ForeignKey(User)  

class UserProfile(models.Model):
    user    = models.OneToOneField(User)
    follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)

class Practise(models.Model):
	course    = models.ForeignKey(Course)
	user      = models.ForeignKey(User)
	quizzes   = models.ManyToManyField(Quiz, related_name='quizzes')
	last_quiz = models.ForeignKey(Quiz)
	
	def populate(self):
		for quiz in self.course.quiz_set.all():
			self.quizzes.add(quiz)

	def top(self):
		return self.last_quiz

	def refresh(self):
		self.quizzes.remove(self.last_quiz)
		if not self.quizzes.all(): # if no quiz left
			self.populate()
		
		try:
			self.last_quiz = self.quizzes.order_by('?')[0]
		except IndexError:
			raise Http404

class Quote(models.Model):
	text = models.CharField(max_length=1000)
	author = models.CharField(max_length=100)

class Book(models.Model):
	name        = models.CharField(max_length=100)
	description = models.CharField(max_length=1000)
	create_date = models.DateTimeField(auto_now=True, blank=True)
	pub_date    = models.DateTimeField('date published')
	creator     = models.CharField(max_length=200, default='Anonymous')

	def __unicode__(self):
		return self.name

class Chapter(models.Model):
	name = models.CharField(max_length=100)
	book = models.ForeignKey(Book)

class Section(models.Model):
	name = models.CharField(max_length=100)
	chapter = models.ForeignKey(Chapter)

class 


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])