#!/usr/bin/env python
import json
import os
import uuid
from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import cv2
import base64
import face_recognition
import asyncio
import threading
from factory.db_connector import SQLiteConnector
from factory.led_manager import LEDCommand
from models.db_models import DbTable
from models.image_models import ImageRequest, ImageResponse, UsersResponse, AttendanceRequest
import time
from io import BytesIO
from PIL import Image
import numpy as np
import base64
from helpers.led_helper import led_device_manager
import signal
import keyboard

from datetime import datetime, timezone, timedelta
from typing import List


############LCD#######################
from time import sleep
from threading import Thread
from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD

from lcd_logic import update_message, start_lcd_thread, stop_lcd_thread

reading = True
message = ""

lcd = LCD()

def safe_exit(signum, frame):
    exit(1)

def display_distance():
    #while reading:
    lcd.text("Alumno" + message, 1)
    lcd.text("Registrado :)", 2)
    sleep(0.25)


'''
    ---------------------------------
    IMPORT IMAGES
    ---------------------------------
'''

def base64_to_image(base64_string):
    # Convert base64 string to image
    _, base64_data = base64_string.split(',', 1)
    image_data = base64.b64decode(base64_data)
    image = Image.open(BytesIO(image_data))
    return np.array(image)


# Load known faces and their names
known_face_encodings = []
known_face_names = []
known_face_groups = []
encodings_lock = threading.Lock()

def load_face_encodings():
    global known_face_encodings, known_face_names, known_face_groups
    # reset face encodings
    known_face_encodings = []
    known_face_names = []
    known_face_groups = []

    print("Importando imágenes...")

    try:
        #connect to database.
        db_connector = SQLiteConnector("app_db.db")
        images_dict = db_connector.get_data_as_dict(table_name=DbTable.BASE64_IMAGES)

        with encodings_lock:
            known_face_encodings = []
            known_face_names = []

            for image_item in images_dict:
                group_id = image_item["group_id"]
                known_image = base64_to_image(image_item["data"])

                # Check if there are faces in the image
                face_encodings = face_recognition.face_encodings(known_image)
                if len(face_encodings) > 0:
                    face_encoding = face_encodings[0]
                    known_face_encodings.append(face_encoding)
                    known_face_names.append(image_item["name"])
                    known_face_groups.append(group_id)
                else:
                    print(f"No se encontró ninguna cara en la imagen para {image_item['name']}")

    except Exception as exp:
        print("Excepción: ", exp)



# load face encodings to begin
load_face_encodings()


# for name in known_face_names:
#     image = face_recognition.load_image_file(f"images/{name}.jpg")  # Replace with the path to your images
#     face_encoding = face_recognition.face_encodings(image)[0]
#     known_face_encodings.append(face_encoding)

print("Starting ...")



'''
    ---------------------------------
    LOAD FAST API
    ---------------------------------
'''

app = FastAPI()

# Socket declarations
ws_app_connection = {}
ws_lock = threading.Lock()

# Serve static files from the "public" folder
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "public"), name="static")

# Serve static files from the "public" folder
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "public"), name="static")

# Define a route to serve the index.html file
@app.get("/")
def read_root():
    return FileResponse(str(Path(__file__).parent / "public" / "index.html"))


# Socket connections
@app.websocket("/ws/{token_guid}")
async def websocket_endpoint(websocket: WebSocket, token_guid: str):
    try:
        await websocket.accept()
        with ws_lock:
            ws_app_connection[token_guid] = websocket
        while token_guid in ws_app_connection:
            # keep socket connection open
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        with ws_lock:
            del(ws_app_connection[token_guid])


@app.get("/recognize")
async def recognize_api():
    global known_face_encodings, known_face_names, known_face_groups

    all_names = []

    with encodings_lock:
        # Capture frame-by-frame
        # Get a reference to webcam #0 (default camera)
        video_capture = cv2.VideoCapture(0)
        ret, frame = video_capture.read()

        # Resize the frame by 1/4 for faster face recognition
        resized_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Find all face locations and face encodings in the current frame
        face_locations = face_recognition.face_locations(resized_frame)
        face_encodings = face_recognition.face_encodings(resized_frame, face_locations)

        name = "Unknown"
        # Loop through each face in the frame
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Check if the face matches any known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = ""

            matched_ids_set = set()
            for match_index, is_match in enumerate(matches):
                try:
                    if is_match:
                        match_group_id = known_face_groups[match_index]
                        if not match_group_id in matched_ids_set:
                            # If a match is found, use the name of the first match
                            if len(name) == 0:
                                name = known_face_names[match_index]
                            else:
                                name = name + ", " + known_face_names[match_index]

                            matched_ids_set.add(match_group_id)
                            set_control_command_for_match(match_group_id)
                except Exception as exp:
                    print("match exeption: ", exp)

            if len(name) == 0:
                name = "Unknown"

            # add to list of all names
            all_names.append(name)

            # Scale the face locations by 4, back to the original frame size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw rectangle and label on the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            text_color = (0, 0, 255)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, text_color, 1)

            video_capture.release()

    # Convert the frame to JPEG format for streaming
    _, buffer = cv2.imencode('.jpg', frame)
    encoded_image = base64.b64encode(buffer).decode('utf-8')

    response_msg = {"image": encoded_image,
                    "names": all_names}
    return JSONResponse(content=response_msg)


@app.get("/images", response_model=list[ImageResponse])
async def get_all_images():
    #connect to database.
    db_connector = SQLiteConnector("app_db.db")
    images_dict = db_connector.get_data_as_dict(table_name=DbTable.BASE64_IMAGES)
    commands_dict = db_connector.get_data_as_dict(table_name=DbTable.COMMANDS)
    users_dict = db_connector.get_data_as_dict(table_name=DbTable.USERS)

    cmd_groups = {}
    for cmd_item in commands_dict:
        group_id = cmd_item["group_id"]
        cmd_groups[group_id] = {}
        cmd_groups[group_id] = cmd_item

    user_groups = {}
    for user_dict in users_dict:
        group_id = user_dict["group_id"]
        user_groups[group_id]={}
        user_groups[group_id]=user_dict
        print("mapping exception: ", user_groups[group_id])

    list_users = {}
    for image_item in images_dict:
        group_id = image_item["group_id"]
        if group_id not in list_users:
            list_users[group_id] = {}
            list_users[group_id]["id"] = group_id
            list_users[group_id]["name"] = image_item["name"]
            list_users[group_id]["base64Images"] = []

            # Verificar si hay un usuario para el group_id actual
            if group_id in user_groups:
                list_users[group_id]["user_fullname"] = user_groups[group_id].get("nombre_completo", "")
                list_users[group_id]["user_university_code"] = user_groups[group_id].get("codigo_universitario", "")
            else:
                # Si no hay usuario, asignar cadenas vacías
                list_users[group_id]["user_fullname"] = ""
                list_users[group_id]["user_university_code"] = ""

            try:
                list_users[group_id]["command_name"] = cmd_groups[group_id]["command_name"]
                list_users[group_id]["device_name"] = cmd_groups[group_id]["device_name"]
            except KeyError as ex:
                print("Error de clave al mapear: ", ex)
            except Exception as ex:
                print("Error desconocido al mapear: ", ex)


        list_users[group_id]["base64Images"].append(image_item["data"])

    #print("Datos enviados:", list_users)

    response_data = list(list_users.values())

    return [ImageResponse(**document) for document in response_data]


#Devolver todas las asistencias por fecha
@app.get("/asistencia/{fecha}", response_model=list[UsersResponse])
async def get_all_assistance_date(fecha:str):

    #connect to database.
    db_connector = SQLiteConnector("app_db.db")
    #images_dict = db_connector.get_data_as_dict(table_name=DbTable.BASE64_IMAGES)
    #commands_dict = db_connector.get_data_as_dict(table_name=DbTable.COMMANDS)
    users_dict = db_connector.get_data_as_dict(table_name=DbTable.USERS)
    asistencia_dict = db_connector.get_data_as_dict(table_name=DbTable.ASISTENCIA)

    print("asistencia_dict:", asistencia_dict)
    # Mapear los usuarios por su group_id
    user_groups = {}
    for user_dict in users_dict:
        user_groups[user_dict["group_id"]] = user_dict

    print("user_groups:", user_groups)
    # Construir la lista de objetos UsersResponse
    users_responses = []
    for asistencia_item in asistencia_dict:
        group_id = asistencia_item["users_idusers"]
        if asistencia_item["fecha"] == fecha:  # Filtrar por fecha de asistencia
            if group_id in user_groups:
                user_data = user_groups[group_id]
                users_responses.append(UsersResponse(
                    id=user_data["idusers"],
                    user_university_code=user_data.get("codigo_universitario", ""),
                    user_fullname=user_data.get("nombre_completo", ""),
                    type_assintance=asistencia_item["tipo_asistencia"]
                ))

    print("asistencias", users_responses)
    return users_responses

def save_asistencia(id_usuario:str, name:str, state:str, fecha:str):
    try:
        # Obtener la fecha actual
        # fecha_actual = datetime.now()
        #Controlar las fechas de entrada: ASISTIÓ - TARDANZA - FALTÓ(En caso no llegue el alumno)
        # Connectar a la base de datos
        db_connector = SQLiteConnector("app_db.db")

        # Verificar si ya existe una asistencia para el usuario en la fecha actual
        existing_asistencia = db_connector.get_data(
            table_name=DbTable.ASISTENCIA,
            condition_dict={"users_idusers": id_usuario, "fecha": fecha}
        )

        # Si ya existe una asistencia para el usuario en la fecha actual, retornar un mensaje de error
        global message
        if existing_asistencia:
            #message = "presente"
            update_message("Alumno:" + name, "Ya Registrado!")
            start_lcd_thread()

            stop_lcd_thread()
        
            print("La asistencia para este usuario ya ha sido registrada hoy.")
            return "La asistencia para este usuario ya ha sido registrada hoy."

        # Si no existe una asistencia para el usuario en la fecha actual, guardar la nueva asistencia
        db_connector.create_or_update(
            table_name=DbTable.ASISTENCIA,
            condition_dict={"idasistencia": str(uuid.uuid4())},
            data={"tipo_asistencia": state,
                  "users_idusers": id_usuario,
                  "fecha": fecha}
        )

        #MOSTAR MENSAJE POR CONSOLA Y DISPLAY
        #message = "presente"

        print("Antes de entrar al display registro")

        update_message("Alumno:" + name, "Registrado!")
        start_lcd_thread()
        stop_lcd_thread()

        print("Asistencia guardada correctamente.")
        return "Asistencia guardada correctamente."
    except Exception as e:
        return f"Error al guardar la asistencia: {str(e)}"


'''
    ---------------------------------
    FALTARÍA AGREGAR UNA FUNCIÓN PARA GUARDAR VARIAS ASISTENCIAS A LA VEZ,
    ENVIADAS DESDE EL FRONTEND
    ---------------------------------
'''

@app.post("/save/image_group/{group_id}", response_model=ImageResponse)
def save_base64_image_api(group_id:str, request_data:ImageRequest):
    print("Llegamos al método guardar")
    #Conectarse a La BD
    db_connector = SQLiteConnector("app_db.db")

    # guardar las imágenes
    for image_data in request_data.base64Images:
        print(image_data)

        db_connector.create_or_update(table_name=DbTable.BASE64_IMAGES,
                                    condition_dict={"id": str(uuid.uuid4())},
                                    data={"group_id": group_id,
                                            "name": request_data.name,
                                            "data": image_data})
    # Guardar comandos
    db_connector.create_or_update(table_name=DbTable.COMMANDS,
                                  condition_dict={"group_id": group_id},
                                  data={"command_name": request_data.command_name,
                                        "device_name": request_data.device_name})

    # Guardar datos del usuario
    db_connector.create_or_update(table_name=DbTable.USERS,
                                  condition_dict={"idusers": str(uuid.uuid4())},
                                  data={"group_id": group_id,
                                        "nombre_completo": request_data.user_fullname,
                                        "codigo_universitario": request_data.user_university_code})

    request_data_dict = request_data.model_dump()

    # Cargar imágenes
    load_face_encodings()

    return ImageResponse(**request_data_dict, id=group_id)

####################################################################
@app.post("/save/attendance")
def save_attendance_api(request_data: List[AttendanceRequest]):
    # Conectarse a la base de datos
    db_connector = SQLiteConnector("app_db.db")

    # Obtener la fecha actual
    fecha_actual = datetime.now()
    fecha_formateada = fecha_actual.strftime("%d-%m-%Y")

    try:
        # Iterar sobre cada AttendanceRequest en la lista
        for attendance_request in request_data:
            print(attendance_request)
            # Obtener el group_id asociado con el codigo_universitario proporcionado por el usuario
            # Obtener el group_id asociado con el codigo_universitario proporcionado por el usuario
            user_data = db_connector.get_data_as_dict(
                table_name=DbTable.USERS,
                condition_dict={"codigo_universitario": attendance_request.user_university_code}
            )
            print("User data")
            print(user_data)

            if user_data:
                # Extraer el group_id del diccionario de datos del usuario
                group_id = user_data[0]["group_id"]
                print(group_id)
                # Actualizar el campo tipo_asistencia en la tabla ASISTENCIA
                db_connector.create_or_update(
                    table_name=DbTable.ASISTENCIA,
                    condition_dict={"users_idusers": group_id, "fecha": fecha_formateada},
                    data={"tipo_asistencia": attendance_request.type_assintance}
                )
            else:
                # El codigo_universitario proporcionado no está asociado con ningún group_id en la tabla USERS
                print(f"El codigo_universitario {attendance_request.user_university_code} no está asociado con ningún group_id en la tabla USERS")

        return {"message": "Asistencias guardadas correctamente"}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
#####################################################################



# delete image by group id
@app.delete("/image/{group_id}")
def delete_image_group_by_id(group_id:str):
    #connect to database.
    db_connector = SQLiteConnector("app_db.db")

    # Eliminar datos relacionados en la tabla users
    db_connector.delete_data(table_name=DbTable.USERS,
                             condition_dict={"group_id": group_id})

    db_connector.delete_data(table_name=DbTable.BASE64_IMAGES,
                             condition_dict={"group_id": group_id})

    db_connector.delete_data(table_name=DbTable.COMMANDS,
                             condition_dict={"group_id": group_id})

    # load latest face encodings
    load_face_encodings()

    return Response(status_code=204)

#####################################################################
def validState(fecha_actual):
    # Verificar si es sábado o domingo (días 5 y 6 correspondientemente)
    if fecha_actual.weekday() in [5, 6]:
        return "FIN DE SEMANA"

    # Establecer las horas de referencia en UTC
    hora_asistio = datetime(fecha_actual.year, fecha_actual.month, fecha_actual.day, 10, 0, 0, tzinfo=timezone.utc)
    hora_tardanza_inicio = datetime(fecha_actual.year, fecha_actual.month, fecha_actual.day, 10, 12, 0, tzinfo=timezone.utc)
    hora_tardanza_fin = datetime(fecha_actual.year, fecha_actual.month, fecha_actual.day, 10, 15, 0, tzinfo=timezone.utc)
    hora_falto = datetime(fecha_actual.year, fecha_actual.month, fecha_actual.day, 10, 15, 1, tzinfo=timezone.utc)

    # Convertir la hora actual a UTC
    fecha_actual_utc = fecha_actual.replace(tzinfo=timezone.utc)

    # Verificar el estado basado en la hora actual
    if hora_asistio <= fecha_actual_utc < hora_tardanza_inicio:
        return "ASISTIÓ"
    elif hora_tardanza_inicio <= fecha_actual_utc < hora_tardanza_fin:
        return "TARDANZA"
    elif fecha_actual_utc >= hora_falto:
        return "FALTA"
    else:
        return "INDEFINIDO"

def run_websocket_image_scan2():
    print("started run_websocket_image_scan 2")
    try:
        consecutive_frames = 0
        user_id_to_save = None

        while True:
            time.sleep(1)

            # if keyboard.is_pressed('q'):
            #     print("Saliendo del bucle...")
            #     break  # Sale del bucle si la tecla 'q' ha sido presionada

            with encodings_lock:
                # Capturar frame por frame
                video_capture = cv2.VideoCapture(0)
                # if video_capture.isOpened():
                #     print(f"La cámara se abrió con el índice 0")
                # else:
                #     print(f"No se pudo abrir la cámara con el índice 0")

                ret, frame = video_capture.read()

                resized_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                face_locations = face_recognition.face_locations(resized_frame)
                face_encodings = face_recognition.face_encodings(resized_frame, face_locations)

                video_capture.release()
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = ""
                    matched_ids_set = set()
                    for match_index, is_match in enumerate(matches):
                        if is_match:
                            match_group_id = known_face_groups[match_index]
                            if not match_group_id in matched_ids_set:
                                user_id_to_save = match_group_id
                                consecutive_frames += 1

                                if consecutive_frames >= 3:
                                    ##CONTROLAR ASISTENCIA POR HORA------------------
                                    # Obtener la fecha actual
                                    fecha_actual = datetime.now()

                                    #Controlar las fechas de entrada: ASISTIÓ - TARDANZA - FALTÓ(En caso no llegue el alumno)
                                    # Formatear la fecha como una cadena con el formato "dd-mm-YYYY"
                                    fecha_formateada = fecha_actual.strftime("%d-%m-%Y")

                                    state = validState(fecha_actual)

                                    print("USUARIO POR REGISTRAR")
                                    name = known_face_names[match_index]
                                    set_control_command_for_match(match_group_id)
                                    save_asistencia(user_id_to_save, name, state, fecha_formateada)
                                    consecutive_frames = 0
                                matched_ids_set.add(match_group_id)
                        # else:
                        #     print("Desconocido")
                        #     update_message("**Desconocido**", "-+-+-+-+-+-+-+-+")
                        #     start_lcd_thread()
                        #     stop_lcd_thread()
                    # if len(name) == 0 or all(match == False for match in matches):
                    #     print("Desconocido")
                    #     update_message("**Desconocido**", "-+-+-+-+-+-+-+-+")
                    #     start_lcd_thread()
                    #     stop_lcd_thread()
                    # if len(name) == 0:
                    #     print("Desconocido")
                    #     update_message("**Desconocido**", "-+-+-+-+-+-+-+-+")
                    #     start_lcd_thread()
                    #     stop_lcd_thread()
                        # name = "Unknown"
    except Exception as e:
        print("Exception:", e)

######################################################################

def run_websocket_image_scan():
    print("started run_websocket_image_scan")
    try:
        while True:
            time.sleep(1)
            # cv2.destroyAllWindows()  # Cierra todas las ventanas abiertas por OpenCV
            # cv2.waitKey(1)
            with encodings_lock:
                # if len() > 0:
                # Capture frame-by-frame
                # Get a reference to webcam #0 (default camera)
                video_capture = cv2.VideoCapture(0)
                ret, frame = video_capture.read()

                # Resize the frame by 1/4 for faster face recognition
                resized_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Find all face locations and face encodings in the current frame
                face_locations = face_recognition.face_locations(resized_frame)
                face_encodings = face_recognition.face_encodings(resized_frame, face_locations)

                name = "Unknown"
                all_names = []
                # Loop through each face in the frame
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # Check if the face matches any known faces
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = ""

                    matched_ids_set = set()
                    for match_index, is_match in enumerate(matches):
                        try:
                            if is_match:
                                match_group_id = known_face_groups[match_index]
                                if not match_group_id in matched_ids_set:
                                    # If a match is found, use the name of the first match
                                    if len(name) == 0:
                                        name = known_face_names[match_index]
                                    else:
                                        name = name + ", " + known_face_names[match_index]

                                    matched_ids_set.add(match_group_id)
                                    # set_control_command_for_match(match_group_id)
                        except Exception as exp:
                            print("match exeption: ", exp)

                    if len(name) == 0:
                        name = "Unknown"

                    # add to list of all names
                    all_names.append(name)

                    # Scale the face locations by 4, back to the original frame size
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    # Draw rectangle and label on the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    text_color = (0, 0, 255)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, text_color, 1)

                # Convert the frame to JPEG format for streaming
                _, buffer = cv2.imencode('.jpg', frame)
                encoded_image = base64.b64encode(buffer).decode('utf-8')

                video_capture.release()

                with ws_lock:
                    if len(ws_app_connection) > 0:
                        for connection_guid, ws_connection in list(ws_app_connection.items()):
                            # Send the encoded image and recognized name to the web interface
                            try:
                                ws_message = {}
                                ws_message["type"] = "image_recognition"
                                ws_message["image"] = encoded_image
                                ws_message["names"] = all_names
                                asyncio.run(ws_connection.send_text(json.dumps(ws_message)))

                                # asyncio.run(ws_connection.send_text(f"{encoded_image},{name}"))
                            except Exception as ex:
                                del(ws_app_connection[connection_guid])
                                print("send websocket exception: ", connection_guid, ": ", ex)

    except Exception as e:
        print("exeption: ", e)


def set_control_command_for_match(match_group_id):
    #connect to database.
    db_connector = SQLiteConnector("app_db.db")
    commands_dict = db_connector.get_data_as_dict(table_name=DbTable.COMMANDS)

    device_cmd = {}
    for cmd_item in commands_dict:
        if cmd_item["group_id"] == match_group_id:
            device_cmd = cmd_item
            break

    if "device_name" in device_cmd:
        led_device_manager.set_command(device_cmd["device_name"], LEDCommand(device_cmd["command_name"]))






