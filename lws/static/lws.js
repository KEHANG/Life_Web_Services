/*
****************************
**** For cook blueprint ****
****************************
*/

function load_items(api_endpoint){
    var items=[];
    $.getJSON(api_endpoint, function(data, status, xhr){
        for (var i = 0; i < data.length; i++ ) {
            items.push(data[i]);
        }
    });
    return items;
};