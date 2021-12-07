#!/usr/bin/env bash

echo -e "\n######### Running CI #########"

echo -e "\n## Running Black ## \n"
black .

echo -e "\n## Running Flake8 ## \n"
flake8

echo -e "\n## Running PyTest and Coverage ## \n"
pytest --cov=src/