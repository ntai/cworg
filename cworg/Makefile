
MANAGE := manage.py

.PHONY: migration run static backup

migration:
	python3 ${MANAGE} makemigrations
	python3 ${MANAGE} migrate

superuser:
	python3 ${MANAGE} createsuperuser --username="cleanwinner" --email="cworg@cleanwinner.com" 

static: common/static/Responsive-Event-Calendar-Date-Picker-jQuery-Plugin-Monthly
	python3 ${MANAGE} collectstatic

run:
	python3 ${MANAGE} runserver 0:3333

backup:
	cd .. && make backup


common/static/Responsive-Event-Calendar-Date-Picker-jQuery-Plugin-Monthly:
	cd common/static && wget https://www.jqueryscript.net/download/Responsive-Event-Calendar-Date-Picker-jQuery-Plugin-Monthly.zip && unzip Responsive-Event-Calendar-Date-Picker-jQuery-Plugin-Monthly.zip && rm -f Responsive-Event-Calendar-Date-Picker-jQuery-Plugin-Monthly.zip


common/static/event-calendar-evo:
	cd common/static && unzip ../../../assetts/event-calendar-evo.zip

reset_migration:
	mysql -u cleanwinner --password="$$CLEANWINNER_PASSWORD" -h mysql.cleanwinner.com cwinner_wednesday < ../reset_migration.sql
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc"  -delete
	make migration superuser
