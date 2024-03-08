
let guid = generateGuid();
var socket = null;

// Function to populate the table with data
function populateTable(data) {
    var tableBody = $('#dynamicTable tbody');
    tableBody.empty(); // Clear existing data
    
    data.forEach(function (img_data) {
        var newRow = $('<tr>');
        newRow.append('<td>' + img_data.name + '</td>');
        // newRow.append('<td>' + img_data.id + '</td>');
        newRow.append('<td>' + (img_data.user_fullname || '-') + '</td>');
        newRow.append('<td>' + (img_data.user_university_code || '-') + '</td>');
        // newRow.append('<td>' + img_data.device_name + '</td>');
        // newRow.append('<td>' + img_data.command_name + '</td>');
        newRow.append('<td><button class="btn btn-danger btn-sm" onclick="deleteGroupData(\'' + img_data.id + '\');" >Eliminar</button></td>');
        tableBody.append(newRow);
    });
}

// Fetch data and populate the table on page load
$(document).ready(function () {
    // Load list of images from api
    getImageGroupsDataFromAPI();
});

// Add an event listener to the document for the custom event
document.addEventListener('reloadHomeDataEvent', function(){
    // Load list of images from api
    getImageGroupsDataFromAPI();
});


document.addEventListener('DOMContentLoaded', function () {
    const wsConnectBtn = document.getElementById('wsConnectBtn');
    const wsDisConnectBtn = document.getElementById('wsDisConnectBtn');

    wsConnectBtn.addEventListener('click', function () {
        connectToImageWebSocket();
    });

    wsDisConnectBtn.addEventListener('click', function () {
        socket.close();
    });
});

function connectToImageWebSocket() {
    let connection_protocol = "ws";
    if (window.location.protocol === "https:") {
        connection_protocol = "wss";
    }

    socket = new WebSocket(connection_protocol + "://" + window.location.host + "/ws/" + guid);
    socket.onmessage = function (event) {
        // var data = event.data.split(',');
        // document.getElementById("video-home").src = "data:image/jpeg;base64," + data[0];
        var msg_data = JSON.parse(event.data);
        if (msg_data.type === "image_recognition"){
            document.getElementById("video-home").src = "data:image/jpeg;base64," + msg_data.image;
        }
    };

    socket.onopen = function (event) {
        const wsConnectBtn = document.getElementById('wsConnectBtn');
        const wsDisConnectBtn = document.getElementById('wsDisConnectBtn');
        const faceDetectVideo = document.getElementById('video-home');

        wsDisConnectBtn.style.display = 'block';
        wsConnectBtn.style.display = 'none';
        faceDetectVideo.style.display = 'block';
    };

    // Define a function to be called when an error occurs
    socket.onerror = function (error) {
        console.error('WebSocket error:', error);
    };

    // Define a function to be called when the WebSocket connection is closed
    socket.onclose = function (event) {
        const wsConnectBtn = document.getElementById('wsConnectBtn');
        const wsDisConnectBtn = document.getElementById('wsDisConnectBtn');
        const faceDetectVideo = document.getElementById('video-home');

        wsDisConnectBtn.style.display = 'none';
        wsConnectBtn.style.display = 'block';
        faceDetectVideo.style.display = 'none';

        console.log('WebSocket connection closed:', event);
    };
}

function loadImageFromAPI() {

    fetch('/recognize', {
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
            console.log('Success:', data);
            document.getElementById("video-home").src = "data:image/jpeg;base64," + data.image;
        })
        .catch(error => {
            // Handle errors
            console.error('Error:', error);
        });
}


function getImageGroupsDataFromAPI() {
    fetch('/images', {
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
            console.log('Success-mostrar:', data);
            populateTable(data)
        })
        .catch(error => {
            // Handle errors
            console.error('Error fatality:', error);
        });
}

function deleteGroupData(id){
    Swal.fire({
        title: '¿Estás seguro?',
        text: '¡Ya no podrás revertir esta acción!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        cancelButtonText: 'CANCELAR',
        confirmButtonText: 'ELIMINAR'
    }).then((result) => {
        if (result.isConfirmed) {
            // User confirmed, perform deletion logic
            deleteGroupFromAPI(id)
        }
    });
}


function deleteGroupFromAPI(id) {
    fetch('/image/' + id, {
        method: 'DELETE',
        body: null,
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            // Check if the response has a body
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                // If there is a JSON body, parse it
                return response.json();
            } else {
                // If there is no body or it's not JSON
                return null;
            }
        })
        .then(data => {
            // Handle the data object
            // console.log('Success:', data);
            getImageGroupsDataFromAPI();
        })
        .catch(error => {
            // Handle errors
            console.error('Error:', error);
        });
}