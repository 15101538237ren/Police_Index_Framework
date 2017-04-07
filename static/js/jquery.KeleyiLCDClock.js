jQuery.fn.KeleyiLCDClock = function(options){
			var $keleyiclock = $(this);
			var defaultOptions = {
				timeText	: $keleyiclock.text(),
			};
			if ($keleyiclock.text()!=""){
				defaultOptions = {timeText : $keleyiclock.text()}
			}
			options = $.extend(defaultOptions,options);
			if (typeof(options.timeText)=="undefined" || options.timeText==""){
				$keleyiclock.text("启动LCD Clock失败！")
			}
			else{
				window.setTimeout(
					function(){
						var time = new Date(options.timeText);
						time.setSeconds( time.getSeconds() + 1 );
						var year = time.getFullYear();
						var month = time.getMonth() + 1;
						var day = time.getDate();
						var hour = time.getHours();
						var minute = time.getMinutes();
						var second = time.getSeconds();
						var time2 = year + "/" + month + "/" + day + " " + hour + ":" + minute + ":" + second;
						options.timeText = time2;
						var html = "";
						var Y1 = Math.floor(year/1000);
						var Y2 = Math.floor((year-1000*Y1)/100);
						var Y3 = Math.floor((year-1000*Y1-100*Y2)/10);
						var Y4 = year%10;
						html += "<span class=\"KeleyiLCDclock\">";
						html += "<span class=\"num" + Y1 + "\"></span><span class=\"num" + Y2 + "\"></span><span class=\"num" + Y3 + "\"></span><span class=\"num" + Y4 + "\"></span><span class=\"year\"></span>";
						html += "<span class=\"num" + Math.floor(month/10) + "\"></span><span class=\"num" + month%10 + "\"></span><span class=\"month\"></span>";
						html += "<span class=\"num" + Math.floor(day/10) + "\"></span><span class=\"num" + day%10 + "\"></span><span class=\"day\"></span>";
						html += "<span class=\"num" + Math.floor(hour/10) + "\"></span><span class=\"num" + hour%10 + "\"></span><span class=\"numseparator\"></span>";
						html += "<span class=\"num" + Math.floor(minute/10) + "\"></span><span class=\"num" + minute%10 + "\"></span><span class=\"numseparator\"></span>";
						html += "<span class=\"num" + Math.floor(second/10) + "\"></span><span class=\"num" + second%10 + "\"></span>";
						html += "</span>";
						$keleyiclock.html(html);
						$keleyiclock.KeleyiLCDClock(options);
					},
					1000
				);
			}
		}