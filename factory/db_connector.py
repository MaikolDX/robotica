from enum import Enum
import sqlite3
import uuid
import threading
from models.db_models import Column, DbTable

class SQLiteConnector:
    def __init__(self, db_file:str):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.lock = threading.Lock()

    def create_table(self, table_name: DbTable, columns: list[Column]):
        with self.lock:
            cursor = self.connection.cursor()

            # Extract primary key columns
            primary_key_columns = [col.name for col in columns if col.primary_key]

            # Generate the columns string
            columns_str = ', '.join(
                [
                    f"{col.name} {col.data_type}{' UNIQUE' if col.unique else ''}"
                    for col in columns
                ]
            )

            # If there is a primary key, adjust the query accordingly
            if primary_key_columns:
                query = f"CREATE TABLE IF NOT EXISTS {table_name.value} ({columns_str}, PRIMARY KEY ({', '.join(primary_key_columns)}))"
            else:
                query = f"CREATE TABLE IF NOT EXISTS {table_name.value} ({columns_str})"

            cursor.execute(query)
            self.connection.commit()

    # def create_table(self, table_name:DbTable, columns:list[Column]):
    #     with self.lock:
    #         cursor = self.connection.cursor()
    #         # columns_example = [Column('id', 'TEXT', primary_key=True, unique=True), Column('name', 'TEXT', unique=True), Column('age', 'INTEGER')]
    #         columns_str = ', '.join([f"{col.name} {col.data_type}{' PRIMARY KEY' if col.primary_key else ''}{' UNIQUE' if col.unique else ''}" for col in columns])
    #         query = f"CREATE TABLE IF NOT EXISTS {table_name.value} ({columns_str})"
    #         cursor.execute(query)
    #         self.connection.commit()

    def add_column(self, table_name:DbTable, new_column:Column):
        with self.lock:
            cursor = self.connection.cursor()
            query = f"ALTER TABLE {table_name.value} ADD COLUMN {new_column.name} {new_column.data_type}"
            cursor.execute(query)
            self.connection.commit()

    def insert_data(self, table_name:DbTable, data:dict):
        with self.lock:
            cursor = self.connection.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in range(len(data))])
            query = f"INSERT INTO {table_name.value} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(data.values()))
            self.connection.commit()

    def get_data_as_dict(self, table_name:DbTable, condition_dict=None):
        with self.lock:
            cursor = self.connection.cursor()
            query = f"SELECT * FROM {table_name.value}"
            if condition_dict:
                condition_str = ' AND '.join([f"{key} = ?" for key in condition_dict.keys()])
                query += f" WHERE {condition_str}"
            
            if condition_dict:
                cursor.execute(query, tuple(condition_dict.values()))
            else:
                cursor.execute(query)

            result_set = cursor.fetchall()

            # Fetch column names
            column_names = [description[0] for description in cursor.description]

            # Combine column names with data into a list of dictionaries
            data_list = [dict(zip(column_names, row)) for row in result_set]

        return data_list
    
    def get_data(self, table_name:DbTable, condition_dict=None):
        cursor = self.connection.cursor()
        query = f"SELECT * FROM {table_name.value}"
        if condition_dict:
            condition_str = ' AND '.join([f"{key} = ?" for key in condition_dict.keys()])
            query += f" WHERE {condition_str}"

        if condition_dict:
            cursor.execute(query, tuple(condition_dict.values()))
        else:
            cursor.execute(query)

        return cursor.fetchall()

    def get_data_sql(self, table_name:DbTable, condition_sql_str=None):
        cursor = self.connection.cursor()
        query = f"SELECT * FROM {table_name.value}"
        if condition_sql_str:
            query += f" WHERE {condition_sql_str}"
        cursor.execute(query)
        return cursor.fetchall()
    
    def create_or_update(self, table_name:DbTable, condition_dict:dict, data:dict):
        existing_data = self.get_data(table_name, condition_dict=condition_dict)
        if existing_data:
            # Data exists, perform update
            self.update_data(table_name, data, condition_dict)
        else:
            # Data doesn't exist, perform insert
            combined_data = {**condition_dict, **data}
            self.insert_data(table_name, combined_data)

    def update_data(self, table_name:DbTable, update_data:dict, condition_dict:dict):
        with self.lock:
            cursor = self.connection.cursor()
            set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
            condition_clause = ' AND '.join([f"{key} = ?" for key in condition_dict.keys()])
            query = f"UPDATE {table_name.value} SET {set_clause} WHERE {condition_clause}"
            cursor.execute(query, tuple(update_data.values()) + tuple(condition_dict.values()))
            self.connection.commit()

    def delete_data_sql(self, table_name:DbTable, condition_sql:str):
        with self.lock:
            cursor = self.connection.cursor()
            query = f"DELETE FROM {table_name.value} WHERE {condition_sql}"
            cursor.execute(query)
            self.connection.commit()

    def delete_data(self, table_name:DbTable, condition_dict:dict):
        with self.lock:
            cursor = self.connection.cursor()
            condition_clause = ' AND '.join([f"{key} = ?" for key in condition_dict.keys()])
            query = f"DELETE FROM {table_name.value} WHERE {condition_clause}"
            cursor.execute(query, tuple(condition_dict.values()))
            self.connection.commit()

    def delete_table(self, table_name:DbTable):
        with self.lock:
            cursor = self.connection.cursor()
            query = f"DROP TABLE IF EXISTS {table_name.value}"
            cursor.execute(query)
            self.connection.commit()

    def close_connection(self):
        with self.lock:
            self.connection.close()


