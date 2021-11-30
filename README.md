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

## Docker deployment

```sh
docker-compose up
```

Use ```docker ps -a``` to list all the containers (or to know their names).

Use ```docker run -it <container name> bash``` to access the terminal of the specified container.

## Heroku deployment

Add the homepage link produced by Heroku to ```ALLOWED_HOSTS``` in ```settings.py```.

Export environment variables for AWS S3.

Then, use the following commands to deploy on Heroku [3]:

```sh
heroku login
heroku create
git push heroku main
heroku ps:scale web=1
heroku open
```

If you want to see all the logs to know and solve problems [4]:

```sh
heroku logs -t 
```

How to access Heroku app console by heroku CLI [5]:

```sh
heroku ps:exec --app=stark-bastion-99715 (The name of the app you want to access)
```

or [6]:

```sh
heroku run bash --app stark-bastion-99715 (The name of the app you want to access)
```

In Heroku CLI, install Pytorch for CPU [7]:

```sh
pip3 install torch==1.9.1+cpu torchvision==0.10.1+cpu torchaudio==0.9.1 -f https://download.pytorch.org/whl/torch_stable.html
```

Exit the CLI:

```sh
exit
```

## Integrate Tailwind CSS with Django:

<ins>**Note:**</ins> The ```theme``` app in this repo has not yet had the folder ```node_modules```. We have to installed NodeJS before running the project.

Follow this [doc](https://django-tailwind.readthedocs.io/en/latest/installation.html) to install Tailwind CSS for a Django project.

And this [doc](https://django-tailwind.readthedocs.io/en/latest/templatetags.html) shows how to include Tailwind's CSS on a page (e.g. ```core/templates/core/preprocess_image.html``` or ```core/templates/core/header.html```).

- These 2 lines are important: add ```{% load tailwind_tags %}``` as the first line of the html file and add ```{% tailwind_css %}``` in the head section.

The ```theme/static_src/tailwind.config.js``` has the ```purge``` attribute for specifying the locations of html files. They will be automatically specified when installing the Tailwind CSS.

```python
    purge: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /* 
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',
        
        /* 
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',
    ],
```

After finishing the above steps, besides a terminal that is for ```make run```, we need another terminal for the (JIT) development server of Tailwind CSS. Run this command so the HTML page will be automatically changed when there is a modification in code:	

```sh
python manage.py tailwind start
```

## References

[1] [Install PostgreSQL on Linux](https://www.postgresqltutorial.com/install-postgresql-linux/), PostgreSQL Tutorial.

[2] [PostgreSQL fatal password authentication failed](https://stackoverflow.com/questions/43060857/postgresql-fatal-password-authentication-failed-for-user-douglas?rq=1), Stackoverflow.

[3] [Deploy the Python app on Heroku](https://devcenter.heroku.com/articles/getting-started-with-python#deploy-the-app), Heroku Dev Center.

[4] [Heroku - how to see all the logs](https://stackoverflow.com/questions/2671454/heroku-how-to-see-all-the-logs), Stackoverflow.

[5] [How to access Heroku app console by heroku CLI](https://stackoverflow.com/questions/62325775/how-to-access-heroku-app-console-by-heroku-cli), Stackoverflow.

[6] [Running bash on Heroku](https://stackoverflow.com/questions/35857787/running-bash-on-heroku-wont-work), Stackoverflow.

[7] [Install Pytorch](https://pytorch.org/), Pytorch.

