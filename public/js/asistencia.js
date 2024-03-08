 // Lista de opciones para el estado
var estados = ["ASISTIÓ", "FALTA", "TARDANZA", "FALTA JUSTIFICADA"];

function populateTable2(data) {
    var tableBody = $('#dynamicTable2 tbody');
    tableBody.empty(); // Limpiar datos existentes

    data.forEach(function (alumno) {
        var newRow = $('<tr>');
        // newRow.append('<td>' + alumno.id + '</td>');
        newRow.append('<td>' + alumno.user_university_code + '</td>');
        newRow.append('<td>' + alumno.user_fullname + '</td>');

        // Crear un elemento select y agregar opciones
        var selectEstado = $('<select>');
        estados.forEach(function (estado) {
            selectEstado.append($('<option>', {
                value: estado,
                text: estado
            }));
        });

        // Seleccionar el estado actual del alumno
        selectEstado.val(alumno.type_assintance);

        // Agregar el select a la fila
        var selectColumn = $('<td>').append(selectEstado);
        newRow.append(selectColumn);

        // Actualizar el estado del alumno cuando se cambie la selección
        selectEstado.change(function () {
            alumno.type_assintance = $(this).val();
        });

        // Botón para eliminar la fila si es necesario
        // newRow.append('<td><button class="btn btn-danger btn-sm" onclick="eliminarAlumno(\'' + alumno.id + '\');" >Eliminar</button></td>');

        // Agregar la fila a la tabla
        tableBody.append(newRow);
    });
}

$(document).ready(function () {
    // Load list of images from api
    $('#irBtn').click(function() {
        var fechaSeleccionada = $('#fechaAsistencia').val(); // Obtener fecha seleccionada
        getStudensAttendanceDataFromAPI(fechaSeleccionada); // Obtener datos de asistencia para la fecha seleccionada
    });
});

document.addEventListener('reloadAssistansEvent', function(){
    // Load list of images from api
    getStudensAttendanceDataFromAPI(fechaSeleccionada);
});

 // Función para obtener los datos actualizados de los alumnos

function obtenerDatosActualizados() {
    var datosActualizados = [];
    $('#dynamicTable2 tbody tr').each(function() {
        // var id = $(this).find('td:eq(0)').text();
        var user_university_code = $(this).find('td:eq(0)').text();
        var user_fullname = $(this).find('td:eq(1)').text();
        var estado = $(this).find('select').val();
        datosActualizados.push({user_university_code: user_university_code, user_fullname: user_fullname, type_assintance: estado});
    });
    return datosActualizados;
}

function saveAllAttendanceToAPI(datosActualizados) {
    console.log(datosActualizados)
    fetch('/save/attendance', {
        method: 'POST',
        body: JSON.stringify(datosActualizados),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Check if the message received is the expected success message
            if (data && data.message === "Asistencias guardadas correctamente") {
                Swal.fire({
                    icon: 'success', // Set the icon type (success, error, warning, info, question, etc.)
                    title: 'Éxito',
                    text: 'Asistencias guardadas',
                });

                // reset view
                getStudensAttendanceDataFromAPI(fechaSeleccionada);
            } else {
                throw new Error("Unexpected response from server");
            }
        })
        .catch(error => {
            // Handle errors
            console.error('Error:', error);
        });
}

// Función para guardar los datos actualizados en el backend
function guardarDatosActualizados() {
    var datosActualizados = obtenerDatosActualizados();
    // Aquí deberías enviar los datos actualizados al backend en una sola solicitud
    saveAllAttendanceToAPI(datosActualizados);
    console.log("Datos actualizados a enviar al backend:", datosActualizados);
}


// Llamar a la función para poblar la tabla con los datos de los alumnos
//populateTable2(obtenerDatosAlumnos());

// Asociar la función de guardar al botón "Guardar"
$('#guardarBtn2').click(function() {
    guardarDatosActualizados();
});


function getStudensAttendanceDataFromAPI(fechaSeleccionada) {

    var formattedDate = formatDate(fechaSeleccionada);

    console.log(formattedDate)

    fetch('/asistencia/' + formattedDate, {
        method: 'GET',
        body: null,
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Handle the data object
            console.log('Success-mostrar-asistencias:', data);
            populateTable2(data)
        })
        .catch(error => {
            // Handle errors
            console.error('Error fatality:', error);
        });
}

function formatDate(date2) {
    var date = new Date(date2);
    // Obtiene los componentes de la fecha
    var day = date.getDate() + 1; //línea 127
    var month = date.getMonth() + 1; // Se agrega 1 ya que los meses van de 0 a 11
    var year = date.getFullYear();

    // Agrega ceros a la izquierda si es necesario para que tengan dos dígitos
    if (day < 10) {
        day = '0' + day;
    }
    if (month < 10) {
        month = '0' + month;
    }

    // Retorna la fecha formateada en formato "dd-mm-yyyy"
    return day + '-' + month + '-' + year;
}
