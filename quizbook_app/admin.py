from django.contrib import admin
from quizbook_app.models import Course, Quiz, QuizRecord, Grade, UserProfile, Practice, Quote

admin.site.register(Course)
admin.site.register(Quiz)
admin.site.register(QuizRecord)
admin.site.register(Grade)
admin.site.register(UserProfile)
admin.site.register(Practice)
admin.site.register(Quote)