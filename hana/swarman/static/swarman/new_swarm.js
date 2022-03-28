function existing_swarm() {

    console.log('Add Existing Swarm')
    container = document.getElementById("swarm_setup")
    let html = `
    <p>
        What is the name of your swarm?
    </p>
    <div class="container container-sm text-center" style="max-width: 500px;" id="">
        <div class="input-group mb-3 flex-nowrap">
            <input type="text" class="form-control" id="swarm_name">
            <button type="button" class="btn btn-primary" onclick="check_swarm_name_existing()">Next</button>
        </div>
        <p id="name_notification"></p>
    </div>
    `;
    container.innerHTML = html;
}


function new_swarm() {
    console.log('Create New Swarm')
}


function check_swarm_name_existing() {
    //Verify name has been entered
    var swarm_name = document.getElementById('swarm_name').value;

    if (swarm_name == "") {

        let notice = document.getElementById("name_notification");
        notice.innerHTML = '<span style="color: red;">Please Enter a name</span>';

    }

    else {

        swarm_name = swarm_name.replace(' ', '+');
        //Attempt to create Swarm name
        $.getJSON(`/swarman/create_swarm?name=${swarm_name}`, function(data) {
            
            //If error message returned, display error message
            if (data.hasOwnProperty('error')) {

                let notice = document.getElementById("name_notification");
                notice.innerHTML = `<span style="color: red;">${data['error']}</span>`;
                
            }
            
            else {
                
                get_swarm_ip_address();
            }
            
            
        });
        
    }
}

function get_swarm_ip_address() {
    //Get the IP Address of the Swarm for nodes to be automatically added
    container = document.getElementById('swarm_setup');

    let html = `
    <p>
        Enter the IP address (or hostname) and API port of your swarm manager.<br>
    </p>
    <p class="fst-italic">
        xxx.xxx.x.xxx:xxxx or hostname:xxxx
    </p>
    <div class="container container-sm text-center" style="max-width: 500px;" id="">
        <div class="input-group mb-3 flex-nowrap">
            <input type="text" class="form-control" id="swarm_address">
            <button type="button" class="btn btn-primary" onclick="get_swarm_data()">Next</button>
        </div>
        <p id="name_notification"></p>
    </div>
    `;
    container.innerHTML = html;

    const csrftoken = getCookie('csrftoken')
    console.log(csrftoken)
}

function get_swarm_data() {
    container = document.getElementById('swarm_setup');

    const swarm_address = document.getElementById('swarm_address').value;

    let html = `
    <p> Fetching node information from http://${swarm_address}...
    `
    container.innerHTML = html;
    //send node information request to a view that will return a formatted JSON object
    // with the Node information retrieved from the
    
}


// This Function needs to be moved to a javascript utils folder
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}