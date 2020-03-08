
# CLEANWINNER_PASSWORD := $(getenv "$CLEANWINNER_PASSWORD")

default:
	echo "Hello"


py3:
	virtualenv -p /usr/bin/python3 py3

tmp/restart.txt:
	mkdir -p tmp
	touch tmp/restart.txt

tmp/Responsive-Event-Calendar-Date-Picker-jQuery-Plugin-Monthly.zip:
	[ -d tmp ] || mkdir -p tmp
	cd tmp && https://www.jqueryscript.net/download/Responsive-Event-Calendar-Date-Picker-jQuery-Plugin-Monthly.zip


bootstrap: tmp/restart.txt py3 
	sudo apt install libmysqlclient-dev
	. py3/bin/activate && pip install pip
	. py3/bin/activate && pip install django mysqlclient

backup:
	[ -d ./backups ] || mkdir -p ./backups
	mysqldump -u cleanwinner --password="$$CLEANWINNER_PASSWORD" -h mysql.cleanwinner.com --add-drop-database --databases cwinner_wednesday > ./backups/cworg.`date +'%Y%m%d_%H%M'`.sql

