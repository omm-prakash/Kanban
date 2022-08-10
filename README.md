# Kanban
A project to manage tasks and pending works.
To see the flowchart of the database visit [here](https://github.com/omm-prakash/Kanban/blob/main/Kanban%20Project.pdf)

# Local Setup
- Clone the project
- Run `bash local_setup.sh`

# Local Development Run
- `bash local_run.sh` It will start the flask app in `development`. Suited for local development

# Replit run
- Go to shell and run
    `pip install --upgrade poetry`
- Click on `main.py` and click button run
- Sample project is at https://replit.com/@thejeshgn/flask-template-app
- The web app will be availabe at https://flask-template-app.thejeshgn.repl.co
- Format https://<replname>.<username>.repl.co

# Folder Structure

- `db_directory` has the sqlite DB. It can be anywhere on the machine. Adjust the path in ``application/config.py`. Repo ships with one required for testing.
- `application` is where our application code is
- `.gitignore` - ignore file
- `local_setup.sh` set up the virtualenv inside a local `.env` folder. Uses `pyproject.toml` and `poetry` to setup the project
- `local_run.sh`  Used to run the flask application in development mode
- `static` - default `static` files folder. It serves at '/static' path. More about it is [here](https://flask.palletsprojects.com/en/2.0.x/tutorial/static/).
- `templates` - Default flask templates folder

