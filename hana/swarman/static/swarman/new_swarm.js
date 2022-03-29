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
    const csrftoken = getCookie('csrftoken')
    

        
    //Attempt to create Swarm name
    $.ajax({
        url: "/swarman/api/swarms/",
        method: "POST",
        dataType: "json",
        data: {
            "swarm_name": swarm_name
        },
        headers: {"X-CSRFToken": csrftoken },
        success: function(data) {
            //Success function happens here
            get_swarm_ip_address();
            },
        error: function(data) {
            //If POST Request fails, display error message
            var parsed_data = JSON.parse(data.responseText)
            let notice = document.getElementById("name_notification");
            notice.innerHTML = `<span style="color: red;">${parsed_data.swarm_name[0]}</span>`        
            }
    });
        
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
    const csrftoken = getCookie('csrftoken')
    const swarm_address = document.getElementById('swarm_address').value;

    let html = `
    <p> Fetching node information from ${swarm_address}...
    `
    container.innerHTML = html;
    //send node information request to a view that will return a formatted JSON object
    // with the Node information retrieved from the
    $.ajax({
        url: "/swarman/api/swarms/existing_swarm_nodes",
        method: "POST",
        dataType: "json",
        data: {
            "swarm_address": swarm_address
        },
        headers: {"X-CSRFToken": csrftoken },
        success: function(data) {
            //Success function happens here
            container = document.getElementById('swarm_setup');
            const nodes = JSON.parse(data)
            console.log(nodes)
            var table = `<p>Discovered Nodes at ${swarm_address}</p>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th scope="col">Hostname</th>
                        <th scope="col">IP Address</th>
                        <th scope="col">Role</th>
                    </tr>
                </thead>
                <tbody>
            `
            console.log(Object.keys(nodes.nodes).length)
            for (var i=0; i<Object.keys(nodes.nodes).length; i++) {
                table += `<tr>
                        <td>${nodes.nodes[i].hostname}</td>
                        <td>${nodes.nodes[i].ip_address}</td>
                        <td>${nodes.nodes[i].role}</td>
                    </tr>
                `
            }
            table += `</tbody></table>`;
            buttons = `<div class="row">
                    <div class="col-4">
                        <button class="btn btn-primary" onclick="get_swarm_ip_address()">Back</button>
                    </div>
                    <div class="col-4">
                        Does node information appear to be correct?
                    </div>
                    <div class="col-4">
                        <button class="btn btn-primary" onclick="">Next</button>
                    </div>
                </div>
            `
            table += buttons
            container.innerHTML = table;
            
        },
        error: function(data) {
            let html = `
                <p>
                Enter the IP address (or hostname) and API port of your swarm manager.<br>
                </p>
                <p class="fst-italic">
                xxx.xxx.x.xxx:xxxx or hostname:xxxx
                </p>
                <div class="container container-sm text-center" style="max-width: 500px;" id="">
                    <div class="input-group mb-3 flex-nowrap">
                        <input type="text" class="form-control" id="swarm_address" value="${swarm_address}">
                        <button type="button" class="btn btn-primary" onclick="get_swarm_data()">Next</button>
                    </div>
                    <p id="name_notification"><span style="color: red;">${data.responseJSON.error}</span></p>
                </div>
            `;
            container.innerHTML = html;
        }
    })
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