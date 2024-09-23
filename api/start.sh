#!/bin/bash

if [ "$API_DEBUG" = "true" ]; then
    exec uvicorn api.app:app --host "$API_HOST" --port "$API_PORT" --reload
else
    exec uvicorn api.app:app --host "$API_HOST" --port "$API_PORT"
fi
