#!/bin/bash

if [ -f /.init_control/run_timestamp ]; then

	echo >&2 "The database was already initialized before. Skipping script execution."

else

	until nc -z db 5432; do
		echo >&2 "Waiting for database"
		sleep 1
	done
	sleep 5

	export PGPASSWORD=$DB_PASSWORD

	echo >&2 "Running 01_create_f1_tables_and_populate.sql"
	psql -h $DB_HOST -U $DB_USER -d $DB_DATABASE -f /queries/01_create_f1_tables_and_populate.sql
	echo >&2 "Running 02_create_users_table_and_triggers.sql"
	psql -h $DB_HOST -U $DB_USER -d $DB_DATABASE -f /queries/02_create_users_table_and_triggers.sql
	echo >&2 "Running 03_create_log_table.sql"
	psql -h $DB_HOST -U $DB_USER -d $DB_DATABASE -f /queries/03_create_log_table.sql
	echo >&2 "Running 04_airports_near_city_function.sql"
	psql -h $DB_HOST -U $DB_USER -d $DB_DATABASE -f /queries/04_airports_near_city_function.sql
	echo >&2 "Running 05_list_drivers.sql"
	psql -h $DB_HOST -U $DB_USER -d $DB_DATABASE -f /queries/05_list_drivers.sql

	date '+%Y%m%d-%H%M%S' > /.init_control/run_timestamp
	echo >&2 "Saving timestamp at /.init_control/run_timestamp. DO NOT DELETE THIS FILE!"

fi
