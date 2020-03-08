#!/bin/sh
exec mysql -u cleanwinner --password="$CLEANWINNER_PASSWORD" -h mysql.cleanwinner.com cwinner_wednesday
