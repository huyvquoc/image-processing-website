# pixm-web

Install required packages for running locally:

```sh
pip install -r requirements_local.txt
```

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
