//$(document).ready(function() {
//   initReturnUrlHref();
//});

$(function(){
    if(typeof JSON == 'undefined'){
        $('head').append($("<script type='text/javascript' src='/static/js/json2.js'>"));
    }
});

function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;

    return [year, month, day].join('-');
}

getUrlParam = function (name,default_param) {
	var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]); 
    return default_param;
}

function clear_state() {
    // sessionStorage.clear();
    //remained those idnex table page numbers
    Object.keys(sessionStorage)
        .filter(function(k) { return (k != "lastpath" && k != "lastpage"); })
        .forEach(function(k) {
        sessionStorage.removeItem(k);
    });

 }

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function initCsrfToken() {
    csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getTableIdSelections(table) {
    return $.map(table.bootstrapTable('getSelections'),
        function(row) {
            return row.id;
        });
}

function getTableUsernameSelections(table) {
    return $.map(table.bootstrapTable('getSelections'),
        function(row) {
            return row.username;
        });
}

function getTableSelections(table) {
    return $.map(table.bootstrapTable('getSelections'),
        function(row) {
            return row;
        });
}

function getTableRowIds(table) {
    return $.map(table.bootstrapTable('getData'),
        function(row) {
            return row.id;
        });
}

function wrapSelections(selections) {
    var today = formatDate(new Date());
    $.each(selections, function(idx, selection) {
        if (selection.total === undefined) {
            selection.total = 0;
            selection.used = 0;
            selection.deadline = today;
        }
    });
    return selections;
}

function get_id() {
    var reg = /(\d+)/;
    return window.location.pathname.match(reg)[0];
}

function get_query_string() {
    var url = window.location.href;
    var offset = url.indexOf("?");
    return url.substr(offset, url.length);
}

function createInfoItem(label, value, status) {
    var item = [];
    item["value"] = value;
    item["label"] = label;
    item["status"] = status;

    return item;
}

function infoItemWrapper(item) {
    var res = [];
    res["body"] = item;
    return res;
}

function bindDate($widget, startdate, enddate) {
    $widget.datetimepicker({
            language: 'zh-CN',
            weekStart: 1,
            todayBtn: 1,
            autoclose: 1,
            todayHighlight: 1,
            startView: 2,
            minView: 2,
            forceParse: 0,
            format: 'yyyy-mm-dd'
        }
    );

    if (arguments[1]) {
        $widget.datetimepicker('setStartDate', new Date(startdate));
    }
    if (arguments[2]) {
        $widget.datetimepicker('setEndDate', new Date(enddate));
    }
    $widget.attr("readonly", true);
}

function bindDateNow($widget) {
    var date = new Date();
    bindDate($widget,date);
}

function getQueryString(){
    var result = location.search.match(new RegExp("[\?\&][^\?\&]+=[^\?\&]+","g"));
    if(result == null){
        return "";
    }

    for(var i = 0; i < result.length; i++){
        result[i] = result[i].substring(1);
    }
    return result;
}

function initReturnUrlHref() {
    var $return_link = $('#return_url');
    if ($return_link.length > 0) {
        $return_link.attr('href', document.referrer)
    }
}

function refreshCaptcha()
{
    var node = document.getElementById('captchaOperation');
    var times = 3000; // gap in Milli Seconds;
    (function startRefresh()
    {
        var address;
        if(node.src.indexOf('?')>-1)
            address = node.src.split('?')[0];
        else
            address = node.src;
        node.src = address+"?time="+new Date().getTime();

    })();
}

function bindPageChange($table, url) {
    var path = window.location.pathname;
    var page = parseInt(getPrePage(path));
    $table.bootstrapTable('refreshOptions', {
        pageNumber: page,
        cache: true,
        url: url
    });
    $table.on('page-change.bs.table', function (e, number) {
        storePrePage(path, number);
    });
}

function storePrePage(path, page) {
    sessionStorage.setItem("lastpath", path);
    sessionStorage.setItem("lastpage", page);
}

function getPrePage(path) {
    var lastpath = sessionStorage.getItem("lastpath");
    if (lastpath === null || lastpath != path)
        return 1;
    return sessionStorage.getItem("lastpage");
}