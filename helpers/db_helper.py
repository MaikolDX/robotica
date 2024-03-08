from factory.db_connector import SQLiteConnector
from models.db_models import Column, DbDataType, DbTable


class DBTableHelper:
    def __init__(self, db_connector:SQLiteConnector):
        self.db_connector = db_connector

    def create_db_tables(self):
        #Creamos la tabla users
        app_columns = [
            Column('idusers', DbDataType.TEXT, primary_key=True),
            Column('group_id', DbDataType.TEXT),
            Column('nombre_completo', DbDataType.TEXT, unique=True),
            Column('codigo_universitario', DbDataType.TEXT, unique=True)
        ]
        # Crea la tabla si no existe
        self.db_connector.create_table(table_name=DbTable.USERS, columns=app_columns)

        # Creación de la tabla asistencia
        app_columns = [
            Column('idasistencia',DbDataType.TEXT, primary_key=True),
            Column('tipo_asistencia', DbDataType.TEXT),
            Column('users_idusers', DbDataType.TEXT),
            Column('fecha', DbDataType.TEXT)
        ]
        # Crea la tabla si no existe
        self.db_connector.create_table(table_name=DbTable.ASISTENCIA, columns=app_columns)

        # # Creación de la tabla fechas
        # app_columns = [
        #     Column('idfechas', DbDataType.INTEGER, primary_key=True),
        #     Column('fecha', DbDataType.TEXT),
        #     Column('comentario', DbDataType.TEXT)
        # ]
        # # Crea la tabla si no existe
        # self.db_connector.create_table(table_name=DbTable.FECHAS, columns=app_columns)

        # create table to store image data
        app_columns = [Column('id', DbDataType.TEXT, primary_key=True, unique=True),
                                Column('group_id', DbDataType.TEXT),
                                Column('name', DbDataType.TEXT),
                                Column('data', DbDataType.TEXT)]

        # creates table if it does not exist.
        self.db_connector.create_table(table_name=DbTable.BASE64_IMAGES, columns=app_columns)

        # create table to command data
        app_columns = [Column('group_id', DbDataType.TEXT, primary_key=True, unique=True),
                                Column('command_name', DbDataType.TEXT),
                                Column('device_name', DbDataType.TEXT)]

        # creates table if it does not exist.
        self.db_connector.create_table(table_name=DbTable.COMMANDS, columns=app_columns)

        # test delete table
        # self.db_connector.delete_table(DbTable.BASE64_IMAGES)