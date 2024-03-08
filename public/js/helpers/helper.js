function generateGuid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}


// Request access to the user's camera
function requestCameraAccessFor(stream_id, deviceId) {
  const video = document.getElementById(stream_id);

  const cameraSelect = document.getElementById('cameraSelect');

  // Define default and less restrictive constraints
  const defaultConstraints = { video: true };
  // Define constraints for a camera with width and height of 1080 pixels
  const hdConstraints = { 
    video: { 
      deviceId: { exact: deviceId},
      width: 1920, 
      height: 1080 
    } 
  };
  const lessRestrictiveConstraints = {
    video: {
      deviceId: { exact: deviceId },
      width: 640, 
      height: 480
    }
  };

  // Try less restrictive constraints first
  navigator.mediaDevices.getUserMedia(hdConstraints)
    .then(function (stream) {
      // If successful, use the stream with less restrictive constraints
      video.srcObject = stream;
    })
    .catch(function (lessRestrictiveError) {
      console.warn('Error with less restrictive constraints:', lessRestrictiveError);

      // If less restrictive constraints fail, try with the specified constraints
      navigator.mediaDevices.getUserMedia(lessRestrictiveConstraints)
        .then(function (stream) {
          video.srcObject = stream;
        })
        .catch(function (finalError) {
          // Show alert
          Swal.fire({
            title: 'Error!',
            html: 'Error accessing the camera. <br>Please grant camera access permissions.',
            icon: 'error',
            confirmButtonText: 'OK'
          });
          console.error('Final error accessing the camera:', finalError);
        });
    });
}


function setElementDisplay() {
  var element = document.getElementById("elementToToggle");

  if (element.style.display === "none" || element.style.display === "") {
      element.style.display = "block";
      element.classList.add("custom-bootstrap-style");
  } else {
      element.style.display = "none";
      element.classList.remove("custom-bootstrap-style");
  }
}