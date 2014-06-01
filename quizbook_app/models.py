import hashlib, sys
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import Http404
from quizbook_app.power import print_terminal
import models_exceptions

class Course(models.Model):
	name        = models.CharField(max_length=100)
	description = models.CharField(max_length=1000)
	create_date = models.DateTimeField(auto_now=True, blank=True)
	pub_date    = models.DateTimeField('date published')
	students    = models.ManyToManyField(User)
	creator     = models.CharField(max_length=200, default='Anonymous')

	def __unicode__(self):
		return self.name

	def count(self):
		return self.quiz_set.count()

	def record_count(self):
		return self.get_records().count()

	def get_quizzes(self):
		return self.quiz_set.all()

	def get_records(self):
		return QuizRecord.objects.filter(quiz__in=self.get_quizzes())

	def update_user_records(self, user):
		for quiz in Quiz.objects.filter(course=self):
			if not QuizRecord.objects.filter(quiz=quiz, user=user):
				record = QuizRecord.objects.create_quiz_record(quiz=quiz, user=user)
				record.save()

	def enroll_user(self, user):
		user.course_set.add(self)
		self.update_user_records(user)

	def drop_user(self, user):
		# delete previous practices for course
		for practice in CoursePractice.objects.filter(course=self, user=user):
			practice.delete()

		user.course_set.remove(self)

	def update_practices_with_quiz(self, quiz):
		for p in CoursePractice.objects.filter(course=self):
			p.add_quiz(quiz)

	def create_quiz(self, question, answer, creator):
		quiz = Quiz(course=self, question=question, creator=creator,
					pub_date=timezone.now())
		quiz.save()
		quiz.add_solution(answer=answer, creator=creator)
		

		self.update_practices_with_quiz(quiz)


	def get_practice_for_user(self, user):
		'''
		Saves the self course and fetches a corresponding Practice
		if it exists, otherwise creates one and returns it.
		'''
		self.save()

		self.update_user_records(user)
		print_terminal("Course count is %d" % self.record_count())

		try:
			# raise Practice.DoesNotExist
			practice = CoursePractice.objects.get(course=self, user=user)
			print_terminal("Retrieving pre-existing practice: [%s]" % str(practice))
		
		except Practice.DoesNotExist:
			practice = CoursePractice(course=self, user=user)
			practice.save()

			for record in self.get_records().filter(user=user):
				print_terminal("Adding record")
				practice.add_quiz_record(record)

			practice.save()
			print_terminal("Creating practice: practice_count[%d], course_count[%d]" % (practice.count(), self.count()))

		
		return practice


class Quiz(models.Model):
	course        = models.ForeignKey(Course)
	question      = models.CharField(max_length=1000)
	creator       = models.CharField(max_length=200, default='Anonymous')
	pub_date      = models.DateTimeField('date published')
	modified_date = models.DateTimeField('date modified', auto_now=True)

	def __unicode__(self):
		return "course[%s], question[%s]" % (unicode(self.course), self.question)

	def update_mod_date(self):
		self.modified_date = timezone.now()
		self.save()

	def get_creator(self):
		return User.objects.get(username=self.creator)

	def get_question(self):
		return self.question

	def get_answer(self):
		return self.get_top_solution().get_text

	def get_course(self):
		return self.course

	def set_question(self, question):
		self.question = question

	def add_solution(self, answer, creator):
		solution = Solution(quiz=self, text=answer, creator=creator)
		solution.save()

	def get_solutions(self):
		return Solution.objects.filter(quiz=self)

	def number_of_solutions(self):
		return len(self.get_solutions())

	def get_top_solution(self):
		return self.get_solution_in_index(0)

	def get_solution_in_index(self, index):
		return self.get_solutions().order_by('-rank')[index]

class QuizRecordManager(models.Manager):
	def create_quiz_record(self, quiz, user):
		"""
		Creates a new QuizRecord, adds a grade 0 to it, and returns the result.
		"""
		quiz_record = self.create(quiz = quiz, user = user)
		grade = Grade(quiz_record = quiz_record, grade = 0)
		grade.save()
		return quiz_record


class QuizRecord(models.Model):
	quiz        = models.ForeignKey(Quiz)
	user        = models.ForeignKey(User)
	created_at  = models.DateTimeField(auto_now_add=True)
	updated_at  = models.DateTimeField(auto_now=True)

	objects = QuizRecordManager()

	def __unicode__(self):
		return "user[%s], quiz[%s]" % (self.user.username, str(self.quiz))

	def calibrate(self):
		pass

	def get_last_grade(self):
		return Grade.objects.filter(quiz_record=self).order_by('-created_at')[0].get_grade()

	def add_grade(self, grade):
		grade = Grade(quiz_record=self, grade=grade)
		grade.save()
		self.update_tokens()

	def update_tokens(self):
		for token in RecordToken.objects.filter(quiz_record=self):
			token.adjust_weight(self.get_last_grade())


class Solution(models.Model):
	quiz = models.ForeignKey(Quiz)
	text = models.TextField()
	rank = models.IntegerField(default=0)
	creator = models.ForeignKey(User)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return "quiz: [%s], rank: [%d], creator: [%s]" % (str(self.get_quiz()), str(self.get_rank()), creator.username)

	def get_quiz(self):
		return self.quiz

	def get_text(self):
		return self.text

	def get_rank(self):
		return self.rank

	def get_creator(self):
		return self.creator

	def set_text(self, text):
		self.text = text
		self.save()

	def increment_rank(self):
		self.set_rank(self.get_rank() + 1)

	def set_rank(self, rank):
		self.rank = rank
		self.save()

	def reset_rank(self):
		self.set_rank(0)

	def rank_is_zero(self):
		return self.get_rank() == 0

	def decrement_rank(self):
		if not self.rank_is_zero():
			self.set_rank(self.get_rank() - 1)


class Grade(models.Model):
	grade       = models.IntegerField(default=0, validators=[lambda x: 0 <= x and x <= 5])
	quiz_record = models.ForeignKey(QuizRecord)
	created_at  = models.DateTimeField(auto_now_add=True)
	updated_at  = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return str(self.get_grade())

	def get_grade(self):
		return self.grade


class UserProfile(models.Model):
	user    = models.OneToOneField(User)
	follows = models.ManyToManyField('self', related_name='followed_by', symmetrical=False)

class Practice(models.Model):
	user          = models.ForeignKey(User)
	
	def __unicode__(self):
		weights = []
		for token in self.get_tokens():
			weights.append(token.get_weight())
		return "user[%s], count[%d], weights%s" % (self.user.username,
													self.count(),
													str(weights))

	def count(self):
		return RecordToken.objects.filter(practice=self).count()

	def is_empty(self):
		return self.count() == 0

	def add_quiz(self, quiz):
		try:
			record = QuizRecord.objects.get(quiz=quiz, user=self.user)
		except:
			record = QuizRecord.objects.create_quiz_record(quiz=quiz, user=self.user)

		self.add_quiz_record(record)

	def add_quiz_record(self, record):
		previous = RecordToken.objects.filter(practice=self, quiz_record=record)
		if previous:
			raise models_exceptions.TokenExistsException

		weight = 0
		token = RecordToken(practice=self, quiz_record=record, weight=weight)
		token.save()

	def top_token(self):
		if self.is_empty():
			raise models_exceptions.PracticeIsEmptyException

		return RecordToken.objects.filter(practice=self).order_by('weight')[0]

	def top_record(self):
		return self.top_token().quiz_record

	def top_quiz(self):
		return self.top_record().quiz

	def pop_quiz(self):
		top_token = self.top_token()
		top_token.adjust_weight(5)
		return top_token.quiz_record.quiz

	def get_tokens(self):
		return RecordToken.objects.filter(practice=self)

	def reset_weights(self):
		for token in self.get_tokens():
			token.weight = 10
			token.save()


class CoursePractice(Practice):
	course = models.ForeignKey(Course)

	def populate(self):
		for quiz in Quiz.objects.filter(course=self):
			self.add_quiz(quiz)


class RecordToken(models.Model):
	practice    = models.ForeignKey(Practice)
	quiz_record = models.ForeignKey(QuizRecord)
	weight      = models.IntegerField(default=0, validators=[lambda x: 0 <= x and x <= 10])

	def __unicode__(self):
		return "practice[%s], quiz_record[%s], weight[%d]" % (str(self.practice), str(self.quiz_record), self.weight)

	def get_weight(self):
		return self.weight

	def adjust_weight(self, weight):
		self.weight = weight
		self.save()


class Quote(models.Model):
	text       = models.CharField(max_length=1000)
	author     = models.CharField(max_length=100)
	rating     = models.IntegerField(default=0, validators=[lambda x: 0 <= x and x <= 5])
	created_at = models.DateTimeField(auto_now_add=True)


class PreambleManager(models.Manager):
	def get_preamble(self):
		try:
			preamble = self.get()
		except:
			preamble = Preamble(text="")
			preamble.save()
		
		return preamble


class Preamble(models.Model):
	text       = models.CharField(max_length=10000)
	updated_at = models.DateTimeField(auto_now=True, blank=True)

	objects = PreambleManager()

	def get_text(self):
		return self.text

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])