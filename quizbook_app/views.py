import sys
import random
import cStringIO as StringIO
import datetime
import os

from django import forms
from django.utils import timezone
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from quizbook_app.forms import AuthenticateForm, UserCreateForm
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from quizbook_app.models import Course, Quiz, Grade, Practise, Quote

def get_quote():
	quote = Quote.objects.order_by('?')[0]
	return '''"%s" (%s)''' % (quote.text, quote.author)

def get_user_or_none(request):
	if request.user.is_authenticated():
		return request.user
	else:
		return None

def get_username_or_anon(user):
	if user != None:
		return user.username
	else:
		return "Anonymous"

def get_or_create_grade(now_user, quiz):
	try:
		grade_model = quiz.grade_set.get(user=now_user)
	except Grade.DoesNotExist:
		grade_model = Grade()
		grade_model.quiz = quiz
		grade_model.user = now_user

	return grade_model

def is_current_user_enrolled(request, course_id):
	return request.user.is_authenticated() and request.user.course_set.filter(pk=course_id)

def index(request):
	latest_course_list = Course.objects.order_by('name')
	user = get_user_or_none(request)
	context = {'latest_course_list': latest_course_list, 'user': user}
	return render(request, 'course_repo.html', context)

def detail(request, course_id, message=None):
	try:
		course = Course.objects.get(pk=course_id)
	except Course.DoesNotExist:
		raise Http404

	user_enrolled = is_current_user_enrolled(request, course_id)
	quizes = course.quiz_set.all()
	user = get_user_or_none(request)
	user_is_creator = False

	if user:
		user_is_creator = (course.creator == user.username)

	context = {
		'course': course,
		'quizes': quizes,
		'error_message': message,
		'user_enrolled': user_enrolled,
		'user': user,
		'user_is_creator': user_is_creator}

	return render(request, 'course_browse.html', context)

def create_restart_practice(request, course_id):
	course = get_object_or_404(Course, pk=course_id)
	user = request.user
	if user.practise_set:
		for practise in user.practise_set.all():
			practise.delete()

	practise           = Practise()
	practise.user      = user
	practise.course    = course
	practise.last_quiz = course.quiz_set.all()[0]
	practise.save()
	practise.populate()
	practise.save()

@login_required
def enroll_user_in_course(request, course_id):
	course = get_object_or_404(Course, pk=course_id)
	
	if not course.quiz_set.all():
		return detail(request, course_id, message="Cannot enroll in empty course.")

	user = request.user
	user.course_set.add(course)

	# remove all previous practises
	create_restart_practice(request, course_id)

	return HttpResponseRedirect(reverse('courses:detail', args=(course_id)))

@login_required
def drop_user_from_course(request, course_id):
	user = request.user
	now_course = get_object_or_404(Course, pk=course_id)
	user.course_set.remove(now_course)

	try:
		practise = user.practise_set.get(course=now_course)
		practise.delete()
	except Practise.DoesNotExist:
		pass

	return HttpResponseRedirect(reverse('courses:detail', args=(course_id)))

def new_course_page(request):
	return render(request, 'create_course.html', {})

def new_course_process(request):
	if request.method != 'POST':
		return HttpResponse("No Form.")
	
	form = NewCourseForm(request.POST)
	if not form.is_valid():
		return HttpResponse("Invalid Form.")

	new_course = Course()
	
	new_course.name        = form.cleaned_data['name']
	new_course.description = form.cleaned_data['description']
	new_course.creator     = get_username_or_anon(get_user_or_none(request))
	new_course.pub_date    = timezone.now()
	
	new_course.save()

	return HttpResponseRedirect(reverse('courses:index', args=()))

def new_quiz_page(request, course_id):
	course = get_object_or_404(Course, pk=course_id)
	user = get_user_or_none(request)
	context = {'course': course, 'user': user}
	return render(request, 'create_quiz.html', context)

def new_quiz_process(request, course_id):
	if request.method != 'POST':
		return HttpResponse("No Form.")
	
	form = NewQuizForm(request.POST)
	if not form.is_valid():
		return HttpResponse("Invalid Form.")

	question = form.cleaned_data['question']
	answer   = form.cleaned_data['answer']
	course = get_object_or_404(Course, pk=course_id)

	if '_submit' in request.POST:
		new_quiz = Quiz()
		new_quiz.course   = course
		new_quiz.question = question
		new_quiz.answer   = answer
		new_quiz.pub_date = timezone.now()

		user = get_user_or_none(request)
		if user:
			new_quiz.creator = user.username

		new_quiz.save()
		return HttpResponseRedirect(reverse('courses:detail', args=(course_id)))
	
	elif '_preview' in request.POST:
		context = {'question': question, 'answer': answer, 'course': course}
		return render(request, 'quiz_preview.html', context)
	

def update_quiz(request, course_id, quiz_id):
	if request.method != 'POST':
		return HttpResponse("No Update Posted.")

	requested = request.POST
	form = UpdateQuizForm(requested)
	if not form.is_valid():
		return HttpResponse("Invalid Form.")

	quiz = get_object_or_404(Quiz, pk=quiz_id)
	now_user = get_user_or_none(request)

	if now_user:
		try:
			grade_model = quiz.grade_set.get(user=now_user)
		except Grade.DoesNotExist:
			grade_model = Grade()
			grade_model.quiz = quiz
			grade_model.user = now_user

		grade_model.grade = form.cleaned_data['grade']
		grade_model.save()
	else:
		# user not logged in
		return HttpResponseRedirect(reverse('home', args=()))

	quiz.modified_date = timezone.now()
	quiz.save()

	return HttpResponseRedirect(reverse('courses:practise', args=(course_id)))

def edit_quiz_page(request, course_id, quiz_id):
	quiz = get_object_or_404(Quiz, pk=quiz_id)
	user = get_user_or_none(request)
	context = {'quiz': quiz, 'user': user}
	return render(request, 'edit_quiz.html', context)

def edit_quiz_process(request, course_id, quiz_id):
	if request.method != 'POST':
		return HttpResponse("No Update Posted.")

	requested = request.POST
	form = EditQuizForm(requested)
	if not form.is_valid():
		return HttpResponse("Invalid Form.")

	quiz = get_object_or_404(Quiz, pk=quiz_id)
	now_user = get_user_or_none(request)

	quiz.question = form.cleaned_data['question']
	quiz.answer = form.cleaned_data['answer']
	quiz.modified_date = timezone.now()
	quiz.save()

	return HttpResponseRedirect(reverse('courses:quiz_page', args=(course_id, quiz_id)))

@login_required
def delete_quiz(request, course_id, quiz_id):
	quiz = get_object_or_404(Quiz, pk=quiz_id)
	if quiz.creator == request.user.username:
		quiz.delete()
	else:
		raise Http404

	return HttpResponseRedirect(reverse('courses:detail', args=(course_id)))

@login_required
def delete_course(request, course_id):
	course = get_object_or_404(Course, pk=course_id)
	if course.creator == request.user.username:
		course.delete()
	else:
		raise Http404

	return HttpResponseRedirect(reverse('courses:index', args=()))

def random_quiz(request, course_id):
	print >>sys.stderr, "IN RANDOM QUIZ"
	try:
		course = Course.objects.get(pk=course_id)
	except Course.DoesNotExist:
		raise Http404

	quizes = course.quiz_set.all()

	try:
		random_quiz = sorted(quizes, key=lambda x: random.random())[0]
		return HttpResponseRedirect(reverse('courses:quiz_page', args=(random_quiz.course.id, random_quiz.id)))
	except IndexError:
		return HttpResponseRedirect(reverse('courses:detail', args=(course_id)))

def quiz(request, course_id):
	chosen = request.POST['quiz']
	course = get_object_or_404(Course, pk=course_id)
	quiz = course.quiz_set.get(pk=chosen)

	quiz.grade += 1
	quiz.save()

	return HttpResponseRedirect('/courses/')

def quiz_page(request, course_id, quiz_id, answer=""):
	quiz = get_object_or_404(Quiz, pk=quiz_id)
	course = Course.objects.get(pk=course_id)
	now_user = get_user_or_none(request)
	user_is_creator = False

	if now_user:
		grade_model = get_or_create_grade(now_user, quiz)
		grade = grade_model.grade
		user_is_creator = (quiz.creator == now_user.username)
	else:
		grade = 0

	user_enrolled = is_current_user_enrolled(request, course_id)
	context = {'quiz': quiz, 'parent_course': course,
		'answer': answer,
		'user': now_user,
		'user_enrolled': user_enrolled,
		'grade': grade,
		'user_is_creator': user_is_creator}

	return render(request, 'quiz_browse.html', context)

def enter_answer(request, quiz_id):
	quiz = get_object_or_404(Quiz, pk=quiz_id)
	answer = request.POST['answer']

	return practise(request, quiz.course.id, answer=answer)

def text_courses(request):
	output = StringIO.StringIO()

	first = True
	for course in Course.objects.all():
		if not first: output.write(("<"*20) + "\n\n")
		else: first = False
		
		output.write((">"*3) + " Course: %s\n\n" % course.name)
		for quiz in course.quiz_set.all():
			star = "Yes" if quiz.star else "No"
			output.write("Question: %s\nAnswer: %s\nGrade: %d; Star: %s\n\n" % (quiz.question, quiz.answer, quiz.grade, star))

	response = HttpResponse(output.getvalue(), content_type='application/force-download')
	response['Content-Length'] = output.tell()
	response['Content-Disposition'] = 'attachment; filename=output.txt'
	return response

def latex_courses(requets):
	output = StringIO.StringIO()
	print >>sys.stderr, str(os.getcwd())
	preamble_file = open("quiz/static/quiz/latex/preamble.txt", "r")

	output.write("\documentclass[12pt]{article}\n\usepackage{amssymb,amsmath,amsthm, amsfonts}\n")
	for line in preamble_file:
		output.write(line)
	output.write("\n")
	preamble_file.close()

	output.write("\n\n\\title{Courses and Quizzes}\n\date{")
	output.write(datetime.datetime.now().strftime("%Y.%m.%d"))
	output.write("}\n\\author{The Quiz Book}\n\\begin{document}\n\maketitle\n\n")
	for course in Course.objects.all():
		output.write("\section{%s}\n\n" % course.name)
		output.write("\\begin{enumerate}\n")
		for quiz in course.quiz_set.all():
			star = "Yes" if quiz.star else "No"
			output.write("\item\n\\textsc{Question:} %s\\\\\n\\\\\n\\textsc{Answer:} %s\\\\\n\\\\\n{\small \\textsc{Grade:} %d; \\textsc{Star:} %s}\\\\\n\n" % (quiz.question, quiz.answer, quiz.grade, star))
		output.write("\end{enumerate}\n\n")
	output.write("\end{document}")
	response = HttpResponse(output.getvalue(), content_type='application/force-download')
	response['Content-Length'] = output.tell()
	response['Content-Disposition'] = 'attachment; filename=output.tex'
	return response

def home(request, auth_form=None, user_form=None, message=None):
	# User is logged in
	if request.user.is_authenticated():
		user = request.user
		courses = user.course_set.order_by('name')

		context = {'user': user,
					   'courses': courses,
					   'next_url': '/'}

		return render(request,
					  'user_page.html', context)
	else:
		# User is not logged in
		auth_form = auth_form or AuthenticateForm()
		user_form = user_form or UserCreateForm()

 		user = get_user_or_none(request)
 		context = {
 			'auth_form': auth_form,
 			'user_form': user_form,
 			'error_message': message,
 			'user': user,
 			'quote': get_quote(),
 			'home': True}

		return render(request, 'start_page.html', context)

def signup(request):
	user_form = UserCreateForm(data=request.POST)
	if request.method == 'POST':
		if user_form.is_valid():
			username = user_form.clean_username()
			password = user_form.clean_password2()
			user_form.save()
			user = authenticate(username=username, password=password)
			login(request, user)
			return redirect('/')
		else:
			return HttpResponse("Invalid Form")
			# return index(request, user_form=user_form)
	return redirect('/')

def login_view(request):
	if request.method == 'POST':
		form = AuthenticateForm(data=request.POST)
		if form.is_valid():
			login(request, form.get_user())
			# Success
			return HttpResponseRedirect(reverse('home', args=()))
		else:
			# Failure
			return home(request, auth_form=form)
	return redirect('/')

def logout_view(request):
	logout(request)
	return HttpResponseRedirect(reverse('home', args=()))

@login_required
def practise(request, course_id, answer=None):
	now_course = get_object_or_404(Course, pk=course_id)

	if not is_current_user_enrolled(request, course_id):
		return HttpResponse("%s is not enrolled in %s" % (user.username, now_course.name))

	user = request.user

	try:
		practise = user.practise_set.get(course=now_course)
	except Practise.DoesNotExist:
		create_restart_practice(request, course_id)
		practise = user.practise_set.get(course=now_course)

	if not answer:
		practise.refresh()
		practise.save()

	quiz = practise.top()
	grade = get_or_create_grade(user, quiz).grade
	return render(request, 'practise_quiz.html',
		{'quiz': quiz,
		'grade': grade,
		'answer': answer})


""" Forms Section """

class NewCourseForm(forms.Form):
	name        = forms.CharField(max_length=100)
	description = forms.CharField(max_length=2000, required=False)


class NewQuizForm(forms.Form):
	question = forms.CharField(max_length=2000)
	answer   = forms.CharField(max_length=2000)

class UpdateQuizForm(forms.Form):
	grade    = forms.IntegerField()

class EditQuizForm(forms.Form):
	question = forms.CharField(max_length=2000)
	answer   = forms.CharField(max_length=2000)