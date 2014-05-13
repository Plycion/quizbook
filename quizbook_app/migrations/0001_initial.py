# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Course'
        db.create_table(u'quizbook_app_course', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('creator', self.gf('django.db.models.fields.CharField')(default='Anonymous', max_length=200)),
        ))
        db.send_create_signal(u'quizbook_app', ['Course'])

        # Adding M2M table for field students on 'Course'
        m2m_table_name = db.shorten_name(u'quizbook_app_course_students')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('course', models.ForeignKey(orm[u'quizbook_app.course'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['course_id', 'user_id'])

        # Adding model 'Quiz'
        db.create_table(u'quizbook_app_quiz', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quizbook_app.Course'])),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=2000)),
            ('creator', self.gf('django.db.models.fields.CharField')(default='Anonymous', max_length=200)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('modified_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'quizbook_app', ['Quiz'])

        # Adding model 'QuizRecord'
        db.create_table(u'quizbook_app_quizrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('quiz', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quizbook_app.Quiz'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'quizbook_app', ['QuizRecord'])

        # Adding model 'Grade'
        db.create_table(u'quizbook_app_grade', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('grade', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('quiz_record', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quizbook_app.QuizRecord'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'quizbook_app', ['Grade'])

        # Adding model 'UserProfile'
        db.create_table(u'quizbook_app_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal(u'quizbook_app', ['UserProfile'])

        # Adding M2M table for field follows on 'UserProfile'
        m2m_table_name = db.shorten_name(u'quizbook_app_userprofile_follows')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_userprofile', models.ForeignKey(orm[u'quizbook_app.userprofile'], null=False)),
            ('to_userprofile', models.ForeignKey(orm[u'quizbook_app.userprofile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_userprofile_id', 'to_userprofile_id'])

        # Adding model 'Practice'
        db.create_table(u'quizbook_app_practice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'quizbook_app', ['Practice'])

        # Adding model 'CoursePractice'
        db.create_table(u'quizbook_app_coursepractice', (
            (u'practice_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['quizbook_app.Practice'], unique=True, primary_key=True)),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quizbook_app.Course'])),
        ))
        db.send_create_signal(u'quizbook_app', ['CoursePractice'])

        # Adding model 'RecordToken'
        db.create_table(u'quizbook_app_recordtoken', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('practice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quizbook_app.Practice'])),
            ('quiz_record', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quizbook_app.QuizRecord'])),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'quizbook_app', ['RecordToken'])

        # Adding model 'Quote'
        db.create_table(u'quizbook_app_quote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'quizbook_app', ['Quote'])


    def backwards(self, orm):
        # Deleting model 'Course'
        db.delete_table(u'quizbook_app_course')

        # Removing M2M table for field students on 'Course'
        db.delete_table(db.shorten_name(u'quizbook_app_course_students'))

        # Deleting model 'Quiz'
        db.delete_table(u'quizbook_app_quiz')

        # Deleting model 'QuizRecord'
        db.delete_table(u'quizbook_app_quizrecord')

        # Deleting model 'Grade'
        db.delete_table(u'quizbook_app_grade')

        # Deleting model 'UserProfile'
        db.delete_table(u'quizbook_app_userprofile')

        # Removing M2M table for field follows on 'UserProfile'
        db.delete_table(db.shorten_name(u'quizbook_app_userprofile_follows'))

        # Deleting model 'Practice'
        db.delete_table(u'quizbook_app_practice')

        # Deleting model 'CoursePractice'
        db.delete_table(u'quizbook_app_coursepractice')

        # Deleting model 'RecordToken'
        db.delete_table(u'quizbook_app_recordtoken')

        # Deleting model 'Quote'
        db.delete_table(u'quizbook_app_quote')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'quizbook_app.course': {
            'Meta': {'object_name': 'Course'},
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.CharField', [], {'default': "'Anonymous'", 'max_length': '200'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'students': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'})
        },
        u'quizbook_app.coursepractice': {
            'Meta': {'object_name': 'CoursePractice', '_ormbases': [u'quizbook_app.Practice']},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quizbook_app.Course']"}),
            u'practice_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['quizbook_app.Practice']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'quizbook_app.grade': {
            'Meta': {'object_name': 'Grade'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'grade': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quiz_record': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quizbook_app.QuizRecord']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'quizbook_app.practice': {
            'Meta': {'object_name': 'Practice'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'quizbook_app.quiz': {
            'Meta': {'object_name': 'Quiz'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quizbook_app.Course']"}),
            'creator': ('django.db.models.fields.CharField', [], {'default': "'Anonymous'", 'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        u'quizbook_app.quizrecord': {
            'Meta': {'object_name': 'QuizRecord'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quiz': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quizbook_app.Quiz']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'quizbook_app.quote': {
            'Meta': {'object_name': 'Quote'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        u'quizbook_app.recordtoken': {
            'Meta': {'object_name': 'RecordToken'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'practice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quizbook_app.Practice']"}),
            'quiz_record': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['quizbook_app.QuizRecord']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'quizbook_app.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'follows': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'followed_by'", 'symmetrical': 'False', 'to': u"orm['quizbook_app.UserProfile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['quizbook_app']