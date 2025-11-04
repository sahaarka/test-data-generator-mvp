@ECHO OFF
cd test_data_generator
set flask_app=app.py
set flask_env=development
start chrome http://127.0.0.1:5000/
flask run
PAUSE