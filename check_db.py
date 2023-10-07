import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('games.db')

# Execute a SELECT query to retrieve the data
query = "SELECT * FROM passes"  # Change 'passes' to your actual table name
df_from_db = pd.read_sql_query(query, conn)

# Close the connection
conn.close()

# Display the retrieved data
print(df_from_db.head())