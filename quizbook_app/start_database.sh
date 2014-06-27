#!/bin/sh

echo 'yes\nplycion\na@a.com\n' > start_database_input.in
python manage.py syncdb < start_database_input.in


echo "execfile('quizbook_app/shell_test.py')\n" > start_database_input.in
python manage.py migrate quizbook_app
python manage.py shell < start_database_input.in

rm start_database_input.in
open 'http://127.0.0.1:8000'
python manage.py runserver