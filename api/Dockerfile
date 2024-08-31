FROM python:3.11-slim

COPY ./api/requirements.txt /requirements.txt

RUN pip install -r requirements.txt

COPY ../database/postgresql_functools.py /database/postgresql_functools.py
COPY ../data/model/random_forest_model.joblib /model/random_forest_model.joblib

CMD if [ "$API_DEBUG" = "true" ]; \
    then uvicorn app:app --host "$API_HOST" --port "$API_PORT" --reload; \
    else uvicorn app:app --host "$API_HOST" --port "$API_PORT"; \
    fi