"""
Customer's database MCP Server
"""
import os
import json

import openai

from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

import dotenv
dotenv.load_dotenv()

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

def generate_sql_query(chat, instructions, user_input):
    """
    Helper function to interact with OpenAI's API for generating SQL query.
    This function now accepts the chat as an argument, which makes it easier
    to replace the chat with a mock during testing.
    """
    response = chat.responses.create(
        model="gpt-4.1",
        instructions=instructions,
        input=user_input
    )
    output = response.output_text.strip()
    if not output:
        raise ValueError("No output from OpenAI API")
    
    sql_query = json.loads(output).get("query", "No query found")
    return sql_query

class MCPServer:
    """
    A class representing the MCP server that handles customer requests.
    It uses OpenAI's API to generate SQL queries based on natural language input.
    The generated SQL queries are executed against a SQLite database, and the results are returned as JSON. 
    """
    def __init__(self, client, db_engine):
        self.client = client
        self.db_engine = db_engine

    def handle_query(self):
        """
        Handle a customer request and generate a SQL query using OpenAI's API.
        The SQL query is then executed against a SQLite database, and the results are returned as JSON.
        """
        data = request.get_json()
        
        query = data.get('message')
        if not query:
            return jsonify({"error": "No query provided"}), 400

        try:
            sql_query = generate_sql_query(self.client, PROMPT_INSTRUCTIONS.strip(), query)

            with self.db_engine.connect() as connection:
                result = connection.execute(text(sql_query))
                rows = [dict(row) for row in result]
            
            return jsonify({"rows": rows})

        except openai.BadRequestError as e:
            return jsonify({"error": str(e)}), 400
        except openai.RateLimitError as e:
            return jsonify({"error": str(e)}), 429
        except SQLAlchemyError as e:
            return jsonify({"error": str(e)}), 500

openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
mcp_server = MCPServer(openai_client, engine)

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
    return mcp_server.handle_query()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
