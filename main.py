"""
Customer's database MCP Server
"""
import os
import openai
import json

from openai.error import InvalidRequestError, RateLimitError
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

import dotenv
dotenv.load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
engine = create_engine('sqlite:///customers.db', echo=True)

PROMPT_INSTRUCTIONS = """
You are an assistant that generates safe, read-only SQL queries for a marketing team.

Rules:
- Only use SELECT statements.
- Never use INSERT, DELETE, UPDATE, DROP, or ALTER.
- Always include a LIMIT clause (default 100).
- Only query from the `customers` table.
- Use standard SQL syntax (SQLite compatible).

Schema:
customers(id, name, email, favorite_genre)

Example:
User: Show all sci-fi readers
SQL: SELECT * FROM customers WHERE favorite_genre = 'Sci-Fi' LIMIT 100;

Return the query in JSON format, like this:
    {"query": "SELECT ..."}
Only provide the JSON response, not explanations.
"""

@app.route('/query', methods=['POST'])
def handle_query():
    """
    Parser a customer request and generate a SQL query using OpenAI's GPT-3.5-turbo model.
    The SQL query is then executed against a SQLite database, and the results are returned as JSON.
    The request should be a JSON object with a 'query' key containing the natural language query.
    Example request:
    {
        "message": "Get all customers who like Fantasy and were created after 2025-01-01"
    }
    Example response:
    {
        "rows": [
            {
                "id": 1,
                "name": "Alice",
                "email": "	alice@example.com"
            }
        ]
    }
    """
    data = request.get_json()
    query = data.get('message')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        response = client.responses.create(
            model="gpt-4.1",
            instructions=PROMPT_INSTRUCTIONS.strip(),
            input=query
        )
    except InvalidRequestError as e:
        return jsonify(query)({"error": str(e)}), 400
    except RateLimitError as e:
        return jsonify({"error": str(e)}), 429

    output = response.output_text.strip()
    sql_query = json.loads(output).get("query", "No query found")

    try:
        # Execute the SQL query
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            rows = [dict(row) for row in result]
        return jsonify(rows)
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
