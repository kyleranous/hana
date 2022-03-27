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
                //If it succeeds, go to next step

            }
            
        });
        
    }
}