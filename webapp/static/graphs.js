
/*
On page load, load interface dropdown with interfaces
avaiable on selected switch.
*/
$( document ).ready(function() {
    var selectedSwitch = $("#node option:selected").val();
    getSwitchInterfaces(selectedSwitch);
    $("#node").change(function() {
        selectedSwitch = $("#node option:selected").val();
        getSwitchInterfaces(selectedSwitch);
    });
});


/*
Function to call switch interface api and handle response 
via the handleAPPResponse callback function
*/
function getSwitchInterfaces(selectedSwitch)
{
    var xhr = new XMLHttpRequest();
    
    if (xhr)
    {
        // open( method, location, isAsynchronous )
        xhr.open("POST", "/switch-interfaces", true);
        // bind callback function
        xhr.onreadystatechange = function()
        {
          handleAPPResponse(xhr, selectedSwitch);
        };
        // actually send the Ajax request 
        var post_params = '{ "switch" : "' + selectedSwitch + '"}';
        xhr.setRequestHeader("Content-type", "application/json");
        xhr.send(post_params); // Send request
    }
}

function handleAPPResponse(xhr, selectedSwitch) {
    if (xhr.readyState == 4 && xhr.status == 200)
    {
        var responseJSON = JSON.parse(xhr.responseText);
        var interfaces = responseJSON['interfaces'];

        var $el = $("#interface");
        $el.empty(); // remove old options
        //push new options
        $.each(interfaces, function(key,value) {
            intVal = value.replace('openflow:'+ selectedSwitch+ ':', "")
            $el.append($("<option></option>")
                .attr("value", intVal).text(value));
        });
    }
}