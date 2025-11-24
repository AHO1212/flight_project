# flight_project
Flight Schedule Parser Project

This program:

Reads a flight CSV file (-i)

Validates data

Saves valid flights into db.json

Saves invalid rows into errors.txt

Runs queries from query.json (-q)

Saves the query result into a response_*.json file

Example:
python3 flight_parser.py -i test.csv -q query.json