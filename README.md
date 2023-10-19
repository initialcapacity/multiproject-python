# Multi-project Python

## Local development
1. Install Python and Poetry
    ```shell
    brew install pyenv
    pyenv install 3.10
    # Add pyenv to the path
    pyenv shell 3.10
    curl -sSL https://install.python-poetry.org | python3 -
    ```

1. Install dependencies

    ```shell
    make install
    ```

1. Set up database

    ```shell
    psql postgres < databases/drop_and_create_databases.sql
    poetry run alembic upgrade head
    DATABASE_URL='postgresql://localhost:5432/starter_test?user=starter&password=starter' poetry run alembic upgrade head
    ```

1. Add a migration

    ```shell
    poetry run alembic revision -m "description"
    ```

1. Check types and run tests

    ```shell
    make test
    ```

1. Check PEP-8 compliance and formatting code

    ```shell
    make check
    ```

1. Reformat code

    ```shell
    make format
    ```

1. Configure .env
  - copy `.env.example` to `.env`

1. Run app

    ```shell
    source .env
    cd applications/starter_app
    poetry run python -m starter_app
    ```

## PyCharm setup

1.  In _Settings → Project: multiproject-python → Python Interpreter_ set the Python interpreter for the top-level
    project to be the existing Python interpreter created via the command line.
1.  Attach each Python subproject to the IDE project with _File → Open... → Attach project..._. Note: On _Open..._, navigate to subproject, click _Open_ and when prompted, click _Attach_. Repeat for each subproject. 
1.  In _Settings → Project: multiproject-python → Python Interpreter_ set the Python interpreter for each Python
    subproject to be the existing Python interpreter created via the command line.
1.  Manually set up dependencies between Python subprojects in _Settings → Project: multiproject-python → Project
    Dependencies_.
    This is clunky, and PyCharm should be able to infer this information from the subprojects' `pyproject.toml` files.
    Watch the [open issue in YouTrack](https://youtrack.jetbrains.com/issue/PY-54269/Imports-from-a-poetry-path-dependency-does-not-resolve)
    for developments.
1.  In _Settings → Tools → Black_ configure PyCharm to use the Black formatter on code reformat and on save.

## Run locally with Docker

```shell
cd applications/starter_app
poetry export --without-hashes -f requirements.txt > ../../requirements.txt
cd ../..
sed -i.backup "s?$(pwd)?/workspace?" requirements.txt
pack build multiproject-python --builder=gcr.io/buildpacks/builder:v1
docker run -p 8080:8080 multiproject-python
```
