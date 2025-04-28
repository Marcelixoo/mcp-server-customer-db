"""
This script sets up a SQLite database with a table for customers.

It creates a table with columns for customer ID, name, email, favorite genre,
and the date they were created.

It also inserts some sample data into the table.
"""

from datetime import date

from sqlalchemy import create_engine, Column, Integer, String, Date, Table, MetaData

engine = create_engine('sqlite:///customers.db', echo=True)
metadata = MetaData()

customers = Table('customers', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('email', String),
    Column('favorite_genre', String),
    Column('created_at', Date, default=date.today)
)

metadata.create_all(engine)

with engine.connect() as connection:
    connection.execute(customers.insert(), [
        {
            "name": "Alice",
            "email": "alice@example.com",
            "favorite_genre": "Fantasy",
            "last_purchase_date": "2025-03-20"
        },
        {
            "name": "Bob",
            "email": "bob@example.com",
            "favorite_genre": "Sci-Fi",
            "last_purchase_date": "2025-04-05"
        },
        {
            "name": "Charlie",
            "email": "charlie@example.com",
            "favorite_genre": "Fantasy",
            "last_purchase_date": "2025-04-01"
        },
        {
            "name": "David",
            "email": "david@example.com",
            "favorite_genre": "Non-fiction",
            "last_purchase_date": "2025-03-18"
        },
        {
            "name": "Eve",
            "email": "eve@example.com",
            "favorite_genre": "Romance",
            "last_purchase_date": "2025-03-22"
        },
        {
            "name": "Frank",
            "email": "frank@example.com",
            "favorite_genre": "Horror",
            "last_purchase_date": "2025-04-07"
        },
        {
            "name": "Grace",
            "email": "grace@example.com",
            "favorite_genre": "Fantasy",
            "last_purchase_date": "2025-04-10"
        },
        {
            "name": "Hannah",
            "email": "hannah@example.com",
            "favorite_genre": "Sci-Fi",
            "last_purchase_date": "2025-04-12"
        },
        {
            "name": "Ivy",
            "email": "ivy@example.com",
            "favorite_genre": "Mystery",
            "last_purchase_date": "2025-03-29"
        },
        {
            "name": "Jack",
            "email": "jack@example.com",
            "favorite_genre": "Fantasy",
            "last_purchase_date": "2025-04-02"
        }
    ])
    connection.commit()
