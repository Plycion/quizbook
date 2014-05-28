import sys
from quizbook_app.models import *
from django.utils import timezone

user = User.objects.get(username="plycion")

for q in Quiz.objects.all():
	answer = q.get_answer()
	q.add_solution(answer)