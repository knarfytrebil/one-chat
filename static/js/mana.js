$('#user_list a').tooltip('show');
//plotting pie chart
function PlotPie(data,place)
{
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

function PlotOverView(data,place)
{
	$.plot($(place), [data],{ 
		series: { 
			lines: { show: true, lineWidth: 1 }, 
			shadowSize: 0 
		},
		xaxis: { 
			ticks: [], mode: "time" 
		}, 
		yaxis: { 
			ticks: [], autoscaleMargin: 0.1 
		},
		selection: { mode: "x" } 
	});
}

//now time
function pubDate()
{
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
//Input Analyze
function analyze(referrer)
{
	var r = "";
	var reCat1 = /one-auction.com/i;
	

	if (referrer == "") {
		r = "直接着陆"
	}else{
		var result = referrer.search(reCat1);	
		switch (result)
		{
			case 7:
				r = "站内";
				break;
			default:
				r = referrer;
		}
	}; 
	return r
}
//Service Message
function service_msg(holder,data)
{
	$(holder).prepend("<li><span class='label'><a href='#' rel='tooltip' title=" + analyze(data.referrer) + ">来源</a></span><a href='javascript:$('#chat').val("+ data.nick + "#);')>" + data.nick + "</a></li>");
	//$("#chattings").prepend("<tr><td><span class='label'>新链接</span><div><i class='icon-time'></i>"+ pubDate()+"</div></td><td><span class='label label-important'>" + data.nick + "</span>&nbsp<span class='label label-warning'>来源：" + analyze(data.referrer) + "</span>&nbsp<span class='label'>当前页面：</span><a href='"+ data.location + "'>"+ data.location +"</a></td></tr>");
	//$(holder).prepend("<tr><td><span class='label'>新链接</span><div><i class='icon-time'></i>"+ pubDate()+"</div></td><td><span class='label'>当前页面</span>&nbsp<a href='"+ data.location + "'>"+ data.location +"</a>&nbsp<span class='label label-important'>" + data.nick + "</span>&nbsp<span class='label label-warning'>" + analyze(data.referrer) + "</span></td></tr>");
}