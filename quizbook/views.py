import cStringIO as StringIO
import datetime
import json
import os
import sys

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from quizbook_app.forms import AuthenticateForm, UserCreateForm, NewCourseForm, NewQuizForm, UpdateQuizForm, EditQuizForm
from quizbook_app.models import Course, Quiz, QuizRecord, Quote, Preamble, Practice
from quizbook_app.power import print_terminal

def get_about(request):
    user = request.user
    context = {"user": user}
    return render(request, 'about.html', context)