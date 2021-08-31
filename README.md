# pixm-web


## Local deployment

### *Required libraries/packages*

First create conda environment and activate it.

Install PostgreSQL:

```sh
sudo apt install postgresql-common
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
pip install psycopg2==2.9.1 || pip install psycopg2-binary
```

Install required packages for running locally:

```sh
pip install -r requirements_local.txt
```

### *Create role for PostgreSQL [1][2]*

To connect to PostgreSQL, need execute commands as ```postgres``` user in Ubuntu:

```sh
sudo -i -u postgres
```

Then, access PostgreSQL by this command:

```sh
psql
```

Now, you can update the authentication database.

Create user:

```sh
CREATE USER huy WITH PASSWORD 'password';
```

or update user's password:

```sh
ALTER USER huy WITH PASSWORD 'password';
```

<ins>**Note:**</ins> The ```USER``` and ```PASSWORD``` of the variable ```DATABASES``` in ```./signup/settings_local.py``` must match the one created in the authentication database.

### *Local running*

For running locally, first need to export to the local setting file:

```sh
export DJANGO_SETTINGS_MODULE=signup.settings_local
```

Then, run the server by:

```sh
make run
```

If you want to update the database:

```sh
make migrate
```

## Heroku deployment

## References

[1] [Install PostgreSQL on Linux](https://www.postgresqltutorial.com/install-postgresql-linux/), PostgreSQL Tutorial.

[2] [PostgreSQL fatal password authentication failed](https://stackoverflow.com/questions/43060857/postgresql-fatal-password-authentication-failed-for-user-douglas?rq=1), Stackoverflow.