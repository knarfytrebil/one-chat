//plotting pie chart
function PlotPie(data,place){
	// DEFAULT
	$.plot($(place), data,
	{
			series: {
				pie: { 
					innerRadius: 0.5,
					show: true
				}
			}
	});
}

//now time
function pubDate(){
	var date = new Date()
	var h = date.getHours(); 
	var m = date.getMinutes(); 
	var se = date.getSeconds(); 
	return (h<10 ? "0"+ h : h) +":" +(m<10 ? "0" + m : m) +":" +(se<10 ? "0" +se : se);
}

function getPrintableDate(date) {
  return date.getFullYear().toString() + '/' +
	 (date.getMonth()+1).toString() + '/' +
	 date.getDate().toString() + ' ' +
	 date.getHours().toString() + ':' +
	 date.getMinutes().toString() + ':' +
	 date.getSeconds().toString() + '.' +
	 date.getMilliseconds().toString();
}

function encodeDate(date)
{
	return [date.getHours(), date.getMinutes(), date.getSeconds(), date.getMilliseconds()];
}

function decodeDate(data)
{
	var date = new Date();
	return new Date(date.getFullYear(), date.getMonth(), date.getDate(),
					data[0], data[1], data[2], data[3]);
}

///Other Functions
function toggleCast()
{	
	$('#casting').button('toggle');
	if (cast == 0) {
		cast = 1;
	}else{
		cast = 0
	};
}