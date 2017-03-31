

function bindPlaceHolder(){
    var userAgent = navigator.userAgent; //取得浏览器的userAgent字符串
    var isOpera = userAgent.indexOf("Opera") > -1; //判断是否Opera浏览器
    var isIE = userAgent.indexOf("compatible") > -1 && userAgent.indexOf("MSIE") > -1 && !isOpera; //判断是否IE浏览器
    if(isIE)
    $('[placeholder]').focus(function() {
      var input = jQuery(this);
      if (input.val() == input.attr('placeholder')) {
        input.val('');
        input.removeClass('placeholder');
      }
    }).blur(function() {
      var input = jQuery(this);
      if (input.val() == '' || input.val() == input.attr('placeholder')) {
        input.addClass('placeholder');
        input.val(input.attr('placeholder'));
      }
    }).blur().parents('form').submit(function() {
      jQuery(this).find('[placeholder]').each(function() {
        var input = jQuery(this);
        if (input.val() == input.attr('placeholder')) {
          input.val('');
        }
      })
    });
}

function loadInfos() {


    var fields = ["id_family_members", "id_education_experience", "id_work_experience", "id_credentials", "id_honor"];

    var $widget = $('#'+fields[0]);
    if ($widget.length > 0 && $widget.val() != "") {
        var $family_members = $.parseJSON($widget.val());
        $.each($family_members, function(idx, value){
            appendFamily(value, false);
        });
    }

    $widget = $('#'+fields[1]);
    if ($widget.length > 0 && $widget.val() != "") {
        var $educations = $.parseJSON($widget.val());
        $.each($educations, function(idx, value){
            appendEdu(value, false);
        });
    }

    $widget = $('#'+fields[2]);
    if ($widget.length > 0 && $widget.val() != "") {
        var $works = $.parseJSON($widget.val());
        $.each($works, function(idx, value){
            appendWork(value, false);
        });
    }

    $widget = $('#'+fields[3]);
    if ($widget.length > 0 && $widget.val() != "") {
        var $cedentials = $.parseJSON($widget.val());
        $.each($cedentials, function(idx, value){
            appendCerf(value, false);
        });
    }

    $widget = $('#'+fields[4]);
    if ($widget.length > 0 && $widget.val() != "") {
        var $honors = $.parseJSON($widget.val());
        $.each($honors, function(idx, value){
            appendHonor(value, false);
        });
    }
    bindPlaceHolder();
}

function appendFamily(values, readonly) {
    operateSpan("family_item", true);
    var length = $('div[id^=family_item]').length;
    if (length >= 5) {
        alert("最多添加5个家庭成员");
        return;
    }
    length += 1;
    var inner = [
        '<div class="row panel-body" id="family_item'+length+'">',
        '<div class="in_box col-lg-1 col-md-1 col-sm-2 col-xs-2">',
        '<h5 id="family_number"'+length+'">'+length+'</h5>',
        '</div>',
        '<div class="in_box col-lg-3 col-md-3 col-sm-3 col-xs-4">',
        '<input type="text" class="form-control" id="family_name'+length+'" placeholder="姓名">',
        '</div>',
        '<div class="in_box col-lg-4 col-md-4 col-sm-4 col-xs-4">',
        '<input type="text" class="form-control" id="family_relation'+length+'" placeholder="关系">',
        '</div>',
        '<div class="in_box col-lg-4 col-md-4 col-sm-6 col-xs-6">',
        '<input type="text" class="form-control" id="family_job'+length+'" placeholder="职业">',
        '</div>',
        '<br>',
        '</div>'
    ].join('');

    var $widget = $(inner);
    if (values.length != 0) {
        var $family_number = $widget.find('#family_number' + length);
        var $family_name = $widget.find('#family_name' + length);
        var $family_relation = $widget.find('#family_relation' + length);
        var $family_job = $widget.find('#family_job' + length);

        $family_number.text(length);
        $family_name.val(values.name);
        $family_relation.val(values.relation);
        $family_job.val(values.job);

        if (readonly) {
            $family_name.attr("readonly", "readonly");
            $family_relation.attr("readonly", "readonly");
            $family_job.attr("readonly", "readonly");
        }
    }

    $('#family_Span').append($widget);
    bindPlaceHolder();
}

function getFamiles() {
    var data = [];
    $('div[id^=family_item]').each(function (idx, vlaue) {
        var item = {};
        var length = idx + 1;
        item["name"] = $(this).find('#family_name' + length).val();
        item["relation"] = $(this).find('#family_relation' + length).val();
        item["job"] = $(this).find('#family_job' + length).val();
        data.push(item);
    });
    return JSON.stringify(data);
}

function appendEdu(values, readonly) {
    operateSpan("edu_item", true);
    var length = $('div[id^=edu_item]').length;
    if (length >= 5) {
        alert("最多添加5项教育经历");
        return;
    }
    length += 1;

    var inner = [
        '<div class="row panel-body" id="edu_item' + length + '" style="text-align:center">',
        '<div class="in_box col-lg-1 col-md-1 col-sm-2 col-xs-2">',
        '<h5 id="edu_number' + length + '">'+length+'</h5>',
        '</div>',
        '<div class="in_box col-lg-2 col-md-2 col-sm-5 col-xs-5">',
        '<input type="text" class="form-control" id="edu_starttime' + length + '" placeholder="开始年-月">',
        '</div>',
        '<div class="in_box col-lg-2 col-md-2 col-sm-5 col-xs-5">',
        '<input type="text" class="form-control" id="edu_endtime' + length + '"  placeholder="结束年-月">',
        '</div>',
        '<div class="in_box col-lg-3 col-md-3 col-sm-4 col-xs-12">',
        '<input type="text" class="form-control" id="edu_school' + length + '" placeholder="毕业院校">',
        '</div>',
        '<div class="in_box col-lg-2 col-md-2 col-sm-4 col-xs-6">',
        '<input type="text" class="form-control" id="edu_major' + length + '"  placeholder="专业">',
        '</div>',
        '<div class="in_box col-lg-2 col-md-2 col-sm-2 col-xs-6">',
        '<select class="form-control" id="edu_degree' + length + '">',
        '<option selected="selected">选择学历...</option>',
        '<option>小学</option><option>初中</option>',
        '<option>高中/中专</option><option>大学专科</option>',
        '<option>大学本科</option><option>硕士</option>',
        '<option>博士</option>',
        '</select>',
        '</div>',
        '<br>',
        '</div>'
    ].join('');

    var $widget = $(inner);
    if (values.length != 0) {
        var $edu_number = $widget.find('#edu_number' + length);
        var $edu_starttime = $widget.find('#edu_starttime' + length);
        var $edu_endtime = $widget.find('#edu_endtime' + length);
        var $edu_school = $widget.find('#edu_school' + length);
        var $edu_major = $widget.find('#edu_major' + length);
        var $edu_degree = $widget.find('#edu_degree' + length);

        $edu_number.val(length);
        $edu_starttime.val(values.starttime);
        $edu_endtime.val(values.endtime);
        $edu_school.val(values.school);
        $edu_major.val(values.major);
        $edu_degree.val(values.degree);

        if (readonly) {
            $edu_starttime.attr("readonly", "readonly");
            $edu_endtime.attr("readonly", "readonly");
            $edu_school.attr("readonly", "readonly");
            $edu_major.attr("readonly", "readonly");
            $edu_degree.attr("disabled", "disabled");
        }
    }

    $('#edu_Span').append($widget);
    bindPlaceHolder();
}

function getEdus() {
    var data = [];
    $('div[id^=edu_item]').each(function (idx, vlaue) {
        var item = {};
        var length = idx + 1;
        item["starttime"] = $(this).find('#edu_starttime' + length).val();
        item["endtime"] = $(this).find('#edu_endtime' + length).val();
        item["school"] = $(this).find('#edu_school' + length).val();
        item["major"] = $(this).find('#edu_major' + length).val();
        item["degree"] = $(this).find('#edu_degree' + length).val();
        data.push(item);
    });
    return JSON.stringify(data);
}

function appendWork(values, readonly) {
    operateSpan("work_item", true);
    var length = $('div[id^=work_item]').length;
    if (length >= 5) {
        alert("最多添加5项目工作经历");
        return;
    }
    length += 1;

    var inner = [
        '<div class="row panel-body" id="work_item' + length + '">',
        '<div class="col-lg-1 col-md-1 col-sm-2 col-xs-2">',
        '<h5 id="work_number'+length+'">'+length+'</h5>',
        '</div>',
        '<div class="in_box col-lg-2 col-md-2 col-sm-5 col-xs-5">',
        '<input type="text" class="form-control" id="work_starttime'+length+'" placeholder="开始年-月">',
        '</div>',
        '<div class="in_box col-lg-2 col-md-2 col-sm-5 col-xs-5">',
        '<input type="text" class="form-control" id="work_endtime'+length+'" placeholder="结束年-月">',
        '</div>',
        '<div class="in_box col-lg-3 col-md-3 col-sm-12 col-xs-12">',
        '<input type="text" class="form-control" id="work_name'+length+'" placeholder="企业名称">',
        '</div>',
        '<div class="in_box col-lg-2 col-md-2 col-sm-6 col-xs-6">',
        '<input type="text" class="form-control" id="work_department'+length+'" placeholder="部门">',
        '</div>',
        '<div class="in_box col-lg-2 col-md-2 col-sm-6 col-xs-6">',
        '<input type="text" class="form-control" id="work_job'+length+'" placeholder="岗位">',
        '</div>',
        '<div class="in_box col-lg-12 col-md-12 col-sm-12 col-xs-12">',
        '<textarea class="form-control" id="work_grade'+length+'" placeholder="请简述您的工作业绩"></textarea>',
        '</div>',
        '</div>'
    ].join('');

    var $widget = $(inner);
    if (values.length != 0) {
        var $work_number = $widget.find('#work_number' + length);
        var $work_starttime = $widget.find('#work_starttime' + length);
        var $work_endtime = $widget.find('#work_endtime' + length);
        var $work_name = $widget.find('#work_name' + length);
        var $work_department = $widget.find('#work_department' + length);
        var $work_job = $widget.find('#work_job' + length);
        var $work_grade = $widget.find('#work_grade' + length);

        $work_number.text(length);
        $work_starttime.val(values.starttime);
        $work_endtime.val(values.endtime);
        $work_name.val(values.name);
        $work_department.val(values.department);
        $work_job.val(values.job);
        $work_grade.val(values.grade);

        if (readonly) {
            $work_starttime.attr("readonly", "readonly");
            $work_endtime.attr("readonly", "readonly");
            $work_name.attr("readonly", "readonly");
            $work_department.attr("readonly", "readonly");
            $work_job.attr("readonly", "readonly");
            $work_grade.attr("readonly", "readonly");
        }
    }

    $('#work_Span').append($widget);
    bindPlaceHolder();
}

function getWorks() {
    var data = [];
    $('div[id^=work_item]').each(function (idx, vlaue) {
        var item = {};
        var length = idx + 1;
        item["starttime"] = $(this).find('#work_starttime' + length).val();
        item["endtime"] = $(this).find('#work_endtime' + length).val();
        item["name"] = $(this).find('#work_name' + length).val();
        item["department"] = $(this).find('#work_department' + length).val();
        item["job"] = $(this).find('#work_job' + length).val();
        item["grade"] = $(this).find('#work_grade' + length).val();
        data.push(item);
    });
    return JSON.stringify(data);
}

function appendCerf(values, readonly) {
    operateSpan("cerf_item", true);
    var length = $('div[id^=cerf_item]').length;
    if (length >= 5) {
        alert("最多添加5个资格选项");
        return;
    }
    length += 1;

    var inner = [
        '<div class="row panel-body" id="cerf_item'+length+'">',
        '<div class="in_box col-lg-1 col-md-1 col-sm-2 col-xs-2">',
        '<h5 id="cerf_number'+length+'">'+length+'</h5>',
        '</div>',
        '<div class="in_box col-lg-4 col-md-4 col-sm-4 col-xs-4">',
        '<input type="text" class="form-control" id="cerf_time'+length+'" placeholder="获得年月">',
        '</div>',
        '<div class="in_box col-lg-7 col-md-7 col-sm-6 col-xs-6">',
        '<input type="text" class="form-control" id="cerf_name'+length+'" placeholder="资格证书名称">',
        '</div>',
        '<br>',
        '</div>'
    ].join('');


    var $widget = $(inner);
    if (values.length != 0) {
        var $cerf_number = $widget.find('#cerf_number' + length);
        var $cerf_time = $widget.find('#cerf_time' + length);
        var $cerf_name = $widget.find('#cerf_name' + length);

        $cerf_number.text(length);
        $cerf_time.val(values.time);
        $cerf_name.val(values.name);

        if (readonly) {
            $cerf_time.attr("readonly", "readonly");
            $cerf_name.attr("readonly", "readonly");
        }
    }
    $('#cer_Span').append($widget);
    bindPlaceHolder();
}

function getCerfs() {
    var data = [];
    $('div[id^=cerf_item]').each(function (idx, vlaue) {
        var item = {};
        var length = idx + 1;
        item["time"] = $(this).find('#cerf_time' + length).val();
        item["name"] = $(this).find('#cerf_name' + length).val();
        data.push(item);
    });
    return JSON.stringify(data);
}

function appendHonor(values, readonly) {
    operateSpan("honor_item", true);
    var length = $('div[id^=honor_item]').length;
    if (length >= 5) {
        alert("最多添加5个荣誉成就");
        return;
    }
    length += 1;

    var inner = [
        '<div class="row panel-body" id="honor_item'+length+'">',
        '<div class="in_box col-lg-1 col-md-1 col-sm-2 col-xs-2">',
        '<h5 id="honor_number'+length+'">'+length+'</h5>',
        '</div>',
        '<div class="in_box col-lg-4 col-md-4 col-sm-4 col-xs-4">',
        '<input type="text" class="form-control" id="honor_time'+length+'" placeholder="获得年月">',
        '</div>',
        '<div class="in_box col-lg-7 col-md-7 col-sm-6 col-xs-6">',
        '<input type="text" class="form-control" id="honor_name'+length+'" placeholder="荣誉或成就详情">',
        '</div>',
        '<br>',
        '</div>',
    ].join('');

    var $widget = $(inner);
    if (values.length != 0) {
        var $honor_number = $widget.find('#honor_number' + length);
        var $honor_time = $widget.find('#honor_time' + length);
        var $honor_name = $widget.find('#honor_name' + length);

        $honor_number.text(length);
        $honor_time.val(values.time);
        $honor_name.val(values.name);

        if (readonly) {
            $honor_time.attr("readonly", "readonly");
            $honor_name.attr("readonly", "readonly");
        }
    }
    $('#honor_Span').append($widget);
    bindPlaceHolder();
}

function getHonors() {
    var data = [];
    $('div[id^=honor_item]').each(function (idx, vlaue) {
        var item = {};
        var length = idx + 1;
        item["time"] = $(this).find('#honor_time' + length).val();
        item["name"] = $(this).find('#honor_name' + length).val();
        data.push(item);
    });
    return JSON.stringify(data);
}

function removeItem(prefix) {
    var length = $('div[id^=' + prefix + ']').length;
    if (length < 1) {
        return;
    } else {
        var id = prefix + length;
        $('div[id=' + id + ']').remove();

        if (length == 1) {
            operateSpan(prefix, false);
        }
    }
}

function operateSpan(prefix, type) {
    switch(prefix[0]) {
        case "e":
            operateSpanItem('edu_Span', type);
            break;
        case "f":
            operateSpanItem('family_Span', type);
            break;
        case "w":
            operateSpanItem('work_Span', type);
            break;
        case "c":
            operateSpanItem('cer_Span', type);
            break;
        case "h":
            operateSpanItem('honor_Span', type);
            break;
        default :
            operateSpanItem('edu_Span', type);
            operateSpanItem('family_Span', type);
            operateSpanItem('work_Span', type);
            operateSpanItem('cer_Span', type);
            operateSpanItem('honor_Span', type);
            break;
    }
}

function operateSpanItem(id, type) {
    if (type) {
        $('#' + id).show();
    } else {
        $('#' + id).hide();
    }

}

function myBrowser(){
    var userAgent = navigator.userAgent; //取得浏览器的userAgent字符串
    var isOpera = userAgent.indexOf("Opera") > -1; //判断是否Opera浏览器
    var isIE = userAgent.indexOf("compatible") > -1 && userAgent.indexOf("MSIE") > -1 && !isOpera; //判断是否IE浏览器
    var isFF = userAgent.indexOf("Firefox") > -1; //判断是否Firefox浏览器
    var isSafari = userAgent.indexOf("Safari") > -1; //判断是否Safari浏览器
    if (isIE) {
        var IE5 = IE55 = IE6 = IE7 = IE8 = IE9 = false;
        var reIE = new RegExp("MSIE (\\d+\\.\\d+);");
        reIE.test(userAgent);
        var fIEVersion = parseFloat(RegExp["$1"]);
        IE55 = fIEVersion == 5.5;
        IE6 = fIEVersion == 6.0;
        IE7 = fIEVersion == 7.0;
        IE8 = fIEVersion == 8.0;
        IE9 = fIEVersion == 9.0;
        if (IE55) {
            return "IE55";
        }
        if (IE6) {
            return "IE6";
        }
        if (IE7) {
            return "IE7";
        }
        if (IE8) {
            return "IE8";
        }
        if(IE9) {
            return "IE9";
        }
    }//isIE end
    if (isFF) {
        return "FF";
    }
    if (isOpera) {
        return "Opera";
    }
}
