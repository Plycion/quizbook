from django.contrib.auth.models import User
from quizbook_app.models import Quiz

user = User.objects.get(username="plycion")

for q in Quiz.objects.all():
    answer = q.get_answer()
    q.add_solution(answer)
