/*
****************************
**** for cook blueprint ****
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
/*
*****************************
**** for stock blueprint ****
*****************************
*/
function setup_charts(dom_id, values, upper_limit) {
	if(dom_id.includes('roi')){
        $('#' + dom_id).sparkline(values,
        	{type: 'line',
		    width: '80',
		    height: '30',
		    normalRangeMin: 0,
		    normalRangeMax: upper_limit,
		    drawNormalOnTop: true});
	}
    else{
    	$('#' + dom_id).sparkline(values,
        	{type: 'line',
		    width: '80',
		    height: '30'});
    }
}