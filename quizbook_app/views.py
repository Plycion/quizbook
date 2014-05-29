import sys
import cStringIO as StringIO
import datetime
import os

from django import forms
from django.db import models
from django.utils import timezone
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from quizbook_app.forms import AuthenticateForm, UserCreateForm
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from quizbook_app.models import Course, Quiz, QuizRecord, Grade, Practice, CoursePractice, Quote, Preamble
from quizbook_app.power import print_terminal
import json

def get_solution(request):
	context = RequestContext(request)
	cat_id = None
	if request.method == 'GET':
		quiz_id = request.GET['quiz_id']
		index = request.GET['index']

	quiz = Quiz.objects.get(id=quiz_id)
	index = int(index)

	solution = quiz.get_solution_in_index(index)
	answer = solution.get_text()

	data = {'answer':answer, 'creator': solution.get_creator().username,
			'rank': solution.get_rank()}

	return HttpResponse(json.dumps(data), content_type = "application/json")

@login_required
def add_solution(request, course_id, quiz_id):
	quiz = Quiz.objects.get(id=quiz_id)
	user = request.user

	context = {'quiz': quiz, 'user': user, 'preamble': get_preamble_text()}
	return render(request, 'create_solution.html', context)

@login_required
def upvote_solution(request, course_id, quiz_id):
	if request.method == 'GET':
		quiz_id = request.GET['quiz_id']
		solution_index = int(request.GET['index'])

	quiz = Quiz.objects.get(id=quiz_id)

	solution = quiz.get_solution_in_index(solution_index)
	solution.increment_rank()

	data = {'new_rank': solution.get_rank()}
	return HttpResponse(json.dumps(data), content_type = "application/json")


@login_required
def process_add_solution(request, course_id, quiz_id):
	quiz = Quiz.objects.get(id=quiz_id)
	answer = request.POST['answer']

	quiz.add_solution(answer, request.user)
	return HttpResponseRedirect(reverse('courses:quiz_page', args=(course_id, quiz_id)))

def get_quote():
	try:
		quote = Quote.objects.order_by('?')[0]
		return '''"%s" (%s)''' % (quote.text, quote.author)
	except:
		return ""

def get_preamble_text():
	return Preamble.objects.get_preamble().get_text()

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

def get_or_create_quiz_record(user, quiz):
	try:
		print_terminal(">>>>> fetched quiz record for user %s" % (user.username))
		quiz_record = QuizRecord.objects.get(user = user, quiz = quiz)
	except QuizRecord.DoesNotExist:
		print >>sys.stderr, ">>>>> created new quiz record for user %s" % (user.username)
		quiz_record = QuizRecord.objects.create_quiz_record(user = user, quiz = quiz)


	return quiz_record

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
	quizes = Quiz.objects.filter(course=course)
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
		'user_is_creator': user_is_creator,
		'preamble': get_preamble_text()}

	return render(request, 'course_browse.html', context)

@login_required
def enroll_user_in_course(request, course_id):
	course = get_object_or_404(Course, pk=course_id)
	
	if not course.quiz_set.all():
		return detail(request, course_id, message="Cannot enroll in empty course.")

	user = request.user
	user.course_set.add(course)

	course.enroll_user(user)
	course.update_user_records(user)

	return HttpResponseRedirect(reverse('courses:detail', args=(course_id)))

@login_required
def drop_user_from_course(request, course_id):
	user = request.user
	course = get_object_or_404(Course, pk=course_id)
	course.drop_user(user)

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

	creator = None
	user = get_user_or_none(request)
	if user:
		creator = user.username

	course.create_quiz(question=question, answer=answer,
						creator=creator)
	return HttpResponseRedirect(reverse('courses:detail', args=(course_id)))

def update_quiz(request, course_id, quiz_id):
	user = get_user_or_none(request)
	if not user:
		return HttpResponseRedirect(reverse('home', args=()))

	if request.method != 'POST':
		return HttpResponse("No Update Posted.")

	requested = request.POST
	form = UpdateQuizForm(requested)
	if not form.is_valid():
		return HttpResponse("Invalid Form.")

	quiz = get_object_or_404(Quiz, pk=quiz_id)
	grade = form.cleaned_data['grade']

	quiz_record = QuizRecord.objects.get(user = user, quiz = quiz)
	quiz_record.add_grade(grade)

	quiz.update_mod_date()

	return HttpResponseRedirect(reverse('courses:practise', args=(course_id)))

def edit_quiz_page(request, course_id, quiz_id):
	quiz = get_object_or_404(Quiz, pk=quiz_id)
	user = get_user_or_none(request)
	context = {'quiz': quiz, 'user': user, 'preamble': get_preamble_text()}
	return render(request, 'edit_quiz.html', context)

def edit_quiz_process(request, course_id, quiz_id):
	if request.method != 'POST':
		return HttpResponse("No Update Posted.")

	requested = request.POST
	form = EditQuizForm(requested)
	if not form.is_valid():
		return HttpResponse("Invalid Form.")

	quiz = get_object_or_404(Quiz, pk=quiz_id)
	user = get_user_or_none(request)

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

def quiz(request, course_id):
	chosen = request.POST['quiz']
	course = get_object_or_404(Course, pk=course_id)
	quiz = course.quiz_set.get(pk=chosen)

	quiz.grade += 1
	quiz.save()

	return HttpResponseRedirect('/courses/')

def quiz_page(request, course_id, quiz_id, answer=""):
	quiz     = get_object_or_404(Quiz, pk=quiz_id)
	course   = Course.objects.get(pk=course_id)
	user     = get_user_or_none(request)

	user_enrolled = is_current_user_enrolled(request, course_id)
	user_is_creator = user and (quiz.creator == user.username)

	if user_enrolled:
		quiz_record = get_or_create_quiz_record(user = user, quiz = quiz)
		grade_list  = quiz_record.grade_set.all()

		sorted_by_date = grade_list.order_by('created_at')

		if not sorted_by_date:
			print >>sys.stderr, ">>>>> empty record for user %s" % (user.username)

		first_grade = list(sorted_by_date)[0]
		last_grade = list(sorted_by_date)[-1]
	else:
		quiz_record = grade_list = first_grade = last_grade = None
	
	context = {'quiz': quiz, 'parent_course': course,
		'answer': answer,
		'user': user,
		'user_enrolled': user_enrolled,
		'quiz_record': quiz_record,
		'grade_list': grade_list,
		'first_grade' : first_grade,
		'last_grade' : last_grade,
		'user_is_creator': user_is_creator,
		'preamble': get_preamble_text(),
		'max': quiz.number_of_solutions()}

	return render(request, 'quiz_browse.html', context)

def enter_answer(request, quiz_id):
	quiz = get_object_or_404(Quiz, pk=quiz_id)
	answer = request.POST['answer']

	return practice(request, quiz.course.id, answer=answer)

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
def practice_answer(request, quiz_id):
	quiz = get_object_or_404(Quiz, pk=quiz_id)
	user = request.user
	answer = request.POST['answer']
	grade = QuizRecord.objects.get(quiz = quiz, user = user).get_last_grade()

	context = {'quiz': quiz, 'grade': grade, 'answer': answer, 'preamble': get_preamble_text()}
	return render(request, 'practice_answer.html', context)

@login_required
def practice_question(request, course_id):
	course = get_object_or_404(Course, pk=course_id)

	if not is_current_user_enrolled(request, course_id):
		return HttpResponse("%s is not enrolled in %s" % (user.username, course.name))

	user = request.user
	practice = course.get_practice_for_user(user)

	print_terminal(str(practice))

	quiz = practice.pop_quiz()
	print_terminal("Popped Quiz: %s" % str(quiz))

	context = {'quiz': quiz, 'preamble': get_preamble_text()}
	return render(request, 'practise_question.html', context)


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