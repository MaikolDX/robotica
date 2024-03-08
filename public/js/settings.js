document.addEventListener('DOMContentLoaded', function () {
    let video = document.getElementById('video-settings');
    let snapshotImg = document.getElementById('snapshot');
    let captureBtn = document.getElementById('captureBtn');
    let selectCameraBtn = document.getElementById('selectCameraBtn');
    let retakeBtn = document.getElementById('retakeBtn');
    let btnSaveRetakeContainer = document.getElementById('btnSaveRetakeContainer');
    let addBtn = document.getElementById('addBtn');
    let saveAllBtn = document.getElementById('saveAllBtn');
    let deleteLastBtn = document.getElementById('deleteLastBtn');
    let cameraDeviceId;
    let minImageAllowed = 1;

    let currentImgData = {};
    let allImages = [];

    // Hide snap shot
    snapshotImg.style.display = 'none';
    setBtnSaveRetakeContainerDisplay('none');

    let stream;
    let cameraSelectorHtml = "";


    // Check if the browser supports the enumerateDevices and getUserMedia APIs
    if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices && navigator.mediaDevices.getUserMedia) {
        // Enumerate the devices and populate the dropdown menu
        navigator.mediaDevices.enumerateDevices()
            .then(function (devices) {
                const cameras = devices.filter(device => device.kind === 'videoinput');

                cameraSelectorHtml = '<select id="camera-selector-id" class="swal2-input">';

                cameras.forEach(function (camera, index) {
                    cameraSelectorHtml = cameraSelectorHtml + '<option value="' + camera.deviceId + '">' + camera.label + ` Camera ${index + 1}` + '</option>';
                });

                cameraSelectorHtml = cameraSelectorHtml + '</select>';

                // Page was reloaded: Check if the URL ends with "/#settings"
                if (window.location.href.endsWith('/#settings')) {
                    // Select Camera...
                    selectSystemCamera();
                }

            })
            .catch(function (error) {
                console.error('Error enumerating devices:', error);
            });
    } else {
        console.error('enumerateDevices or getUserMedia is not supported in this browser');
    }


    // Stop camera stream
    function stopCameraStream() {
        stream = video.srcObject
        // Stop the current media stream
        if (stream) {
            const tracks = stream.getTracks();
            tracks.forEach(track => track.stop());
        }
    }


    // Capture snapshot when the "Capture" button is clicked
    captureBtn.addEventListener('click', function () {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        // Set the canvas dimensions to match the video dimensions
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Draw the current frame from the video onto the canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert the canvas content to base64 with JPG format
        const base64Snapshot = canvas.toDataURL('image/jpeg');

        // Display the snapshot as an image
        snapshotImg.src = base64Snapshot;

        // Hide the video element
        snapshotImg.style.display = 'block';
        setBtnSaveRetakeContainerDisplay('block');
        captureBtn.style.display = 'none';
        selectCameraBtn.style.display = 'none';
        video.style.display = 'none';

        currentImgData.base64Snapshot = base64Snapshot;

        // Stop the current media stream
        stopCameraStream();

    });

    // Retake the current camera view when the "Retake" button is clicked
    retakeBtn.addEventListener('click', function () {
        retakeSnapshots();
    });

    // on selectCameraBtn click
    selectCameraBtn.addEventListener('click', function () {
        selectSystemCamera();
    });

    // on addBtn click
    addBtn.addEventListener('click', function () {
        allImages.push(JSON.parse(JSON.stringify(currentImgData)));
        loadAllImages();
    });

    // on deleteLastBtn click
    deleteLastBtn.addEventListener('click', function () {
        if (allImages.length > 0) {
            allImages.pop();
            loadAllImages();
        }
    });

    // on saveAllBtn click
    saveAllBtn.addEventListener('click', function () {
        if (allImages.length < minImageAllowed) {
            Swal.fire({
                icon: 'error', // Set the icon type (success, error, warning, info, question, etc.)
                title: 'Error',
                text: 'Add more images. At least "'+ minImageAllowed +'" image[s] is required.',
            });

            return;
        }

        Swal.fire({
            title: 'Datos del Usuario',
            html:
                '<input id="swal-input1" class="swal2-input" placeholder="Ingresa un nombre de usuario">' +
                '<input id="swal-input4" class="swal2-input" placeholder="Ingresa tu nombre completo">' +
                '<input id="swal-input5" class="swal2-input" placeholder="Ingresa tu código universitario">',
            showCancelButton: true,
            confirmButtonText: 'GUARDAR',
            cancelButtonText: 'CANCELAR',
            preConfirm: () => {
                const inputName = document.getElementById('swal-input1').value;
                const inputUniversityCode = document.getElementById('swal-input5').value;
                const inputFullName = document.getElementById('swal-input4').value;
                // const inputDevice = document.getElementById('swal-input2').value;
                // const inputAction = document.getElementById('swal-input3').value;

                if (inputName && inputUniversityCode && inputFullName) {
                    return { inputName, inputUniversityCode, inputFullName};
                } else {
                    Swal.showValidationMessage('Por favor, completa todos los campos');
                }
                // if (inputName && inputDevice && inputAction && inputUniversityCode && inputFullName) {
                //     return { inputName, inputDevice, inputAction, inputUniversityCode, inputFullName};
                // } else {
                //     Swal.showValidationMessage('Por favor, completa todos los campos');
                // }
            },
        }).then((result) => {
            if (result.isConfirmed) {
                let img_list = [];
                for (let img of allImages) {
                    img_list.push(img.base64Snapshot);
                }

                img_request_data = {
                    "name": result.value.inputName,
                    "command_name": 'ON',
                    "device_name": 'GREEN_LED',
                    "base64Images": img_list,
                    "user_university_code": result.value.inputUniversityCode,
                    "user_fullname": result.value.inputFullName
                };
                console.log('Datos a enviar al backend:', img_request_data);
                saveAllImagesToAPI(img_request_data);
            } else {
                Swal.fire('Se canceló el guardado');
            }
        });
    });

    function resetSettingsViewAddAllImageData() {
        allImages = [];
        loadAllImages();
    }



    function loadAllImages() {
        for (let i = 0; i < 8; i++) {
            let savedImg = document.getElementById('saved-img-' + i);
            if (i < allImages.length) {
                savedImg.src = allImages[i].base64Snapshot;
            } else {
                savedImg.src = "./static/images/default_image.png";
            }

        }

        retakeSnapshots();
    }

    function retakeSnapshots() {
        // Show the video element
        snapshotImg.style.display = 'none';
        setBtnSaveRetakeContainerDisplay('none');
        captureBtn.style.display = 'block';
        selectCameraBtn.style.display = 'block';
        video.style.display = 'block';

        // Reset the image source
        snapshotImg.src = '';

        // Stop the current media stream
        stopCameraStream();

        // Request access to the user's camera again
        requestCameraAccessFor('video-settings', cameraDeviceId);
    }


    function saveAllImagesToAPI(img_request_data) {
        let guid = generateGuid();
        console.log("GROUP_ID GENERADO")
        console.log(guid)

        fetch('/save/image_group/' + guid, {
            method: 'POST',
            body: JSON.stringify(img_request_data),
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
                // Handle the data object
                Swal.fire({
                    icon: 'success', // Set the icon type (success, error, warning, info, question, etc.)
                    title: 'Guardado',
                    text: 'El alumno fue registrado con éxito!',
                });

                // reset view
                resetSettingsViewAddAllImageData();

            })
            .catch(error => {
                // Handle errors
                console.error('Error:', error);
            });
    }


    // Add an event listener to the document for the custom event
    document.addEventListener('cameraSelectorEvent', function () {
        if (cameraDeviceId == null){
            selectSystemCamera();
        }
    });


    function selectSystemCamera() {
        Swal.fire({
            title: 'Selecciona una cámara',
            html: cameraSelectorHtml,
            showCancelButton: false,
            confirmButtonText: 'Seleccionar',
            cancelButtonText: 'Cancelar',
            preConfirm: () => {
                cameraDeviceId = document.getElementById('camera-selector-id').value;
                return { cameraDeviceId };
            },
        }).then((result) => {
            stopCameraStream("video-settings");
            requestCameraAccessFor('video-settings', result.value.cameraDeviceId)
        });
    }

    function setBtnSaveRetakeContainerDisplay(value){
        addBtn.style.display = value;
        retakeBtn.style.display = value;
    }


});