import sys
from quizbook_app.models import *
from django.utils import timezone

user = User.objects.get(username="plycion")

c1 = Course(name="c1", pub_date=timezone.now())
c2 = Course(name="c2", pub_date=timezone.now())

c1.save()
c2.save()

c1.create_quiz(question="What is 2+2", answer="4", creator=user)
c2.create_quiz(question="What is 3+2", answer="5", creator=user)

# p = Practice(user=user)

# p.save()

# p.add_quiz_record(r1)
# p.add_quiz_record(r2)

# t1 = RecordToken.objects.get(quiz_record=r1)
# t2 = RecordToken.objects.get(quiz_record=r2)

# t1.weight = 0
# t2.weight = 10

# t1.save()
# t2.save()


# p.save()

# print "Records: %s" % str(RecordToken.objects.filter(practice=p))


# print p.is_empty()

# quiz = p.pop_quiz()
# print str(quiz)

# quiz = p.pop_quiz()
# print str(quiz)

# arg = sys.argv[1]

# agr = "-d"
# if arg == "-d":
# 	p.delete()

# 	r1.delete()
# 	r2.delete()

# 	q1.delete()
# 	q2.delete()

# 	c1.delete()
# 	c2.delete()