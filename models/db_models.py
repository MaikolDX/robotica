from enum import Enum

class DbTable(Enum):
    BASE64_IMAGES = "b64_images"
    COMMANDS = "commands"
    USERS = "users_table"
    ASISTENCIA = "asistencia"
    #Aca se crean las tablas de la base de datos, es decir, se crea una clase que hereda de Enum, y se le asigna el nombre de la tabla.

class DbDataType(Enum):
    NULL = "NULL"
    INTEGER = "INTEGER"
    REAL = "REAL"
    TEXT = "TEXT"
    BLOB = "BLOB"
    NUMERIC = "NUMERIC"

class Column:
    def __init__(self, name:str, data_type:DbDataType, primary_key=False, unique=False):
        self.name = name
        self.data_type = data_type.value
        self.primary_key = primary_key
        self.unique = unique