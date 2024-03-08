
// var tabs = ['home', 'settings', 'contact', 'about'];
const tabs = ['home', 'settings', 'asistencia'];

// Define a custom event
const reloadHomeDataEvent = new Event('reloadHomeDataEvent');
const cameraSelectorEvent = new Event('cameraSelectorEvent');
const reloadAssistansEvent = new Event('reloadAssistansEvent');



// Function to trigger the custom event
function triggerReloadHomeDataEvent() {
    document.dispatchEvent(reloadHomeDataEvent);
}

// Function to trigger the custom event
function triggerCameraSelectorEvent() {
    document.dispatchEvent(cameraSelectorEvent);
}
function triggerreloadAssistansEvent() {
    document.dispatchEvent(reloadAssistansEvent);
}

// Stop camera stream
function stopCameraStream(streamId) {
    const video = document.getElementById(streamId);
    let stream = video.srcObject

    // Stop the current media stream
    if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
    }
}

function setReloadedTab() {
    for (let tab of tabs) {
        if (window.location.href.includes('#' + tab)) {
            showContent(tab);
            return;
        }
    }

    let hrefLink = "#" + tabs[0];
    window.location.href = hrefLink;
    setReloadedTab();
}

setReloadedTab();


function showContent(tab) {
    // Hide all content divs
    document.getElementById('homeContent').style.display = 'none';
    document.getElementById('settingsContent').style.display = 'none';
    document.getElementById('contactContent').style.display = 'none';
    document.getElementById('aboutContent').style.display = 'none';
    document.getElementById('asistenciaContent').style.display = 'none';

    // Show the selected content div
    document.getElementById(tab + 'Content').style.display = 'block';

    // Update the active tab
    tabs.forEach(function (t) {
        var link = document.querySelector('.topnav a[href="#' + t + '"]');
        link.classList.remove('active');
    });
    document.querySelector('.topnav a[href="#' + tab + '"]').classList.add('active');

    // Home tab selected, enable camera for home-tab
    if (tab === "home") {
        // Call the function to trigger the event
        triggerReloadHomeDataEvent();
    }


    if (tab === "settings") {
        // Do nothing
        // requestCameraAccessFor("video-settings");
        triggerCameraSelectorEvent();
    } 
    
    if(tab === "asistencia"){
        triggerreloadAssistansEvent();
    }
    else {
        try {
            stopCameraStream("video-settings");
        } catch (error) {
            console.log("settings camera stream may be offline.")
        }
    }

}