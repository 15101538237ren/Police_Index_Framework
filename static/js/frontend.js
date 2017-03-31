var page_num, step, total_num, total_time, category, value, url, quiz_id, msg, last, required, score, typesetting;
var _category = ["","单选题","简答题","赋分题"];
var answer = [];
var status = 0;
var csrftoken;

$(function(){
    quiz_id = $("#quiz_id").val();
    url = "/frontend/" + quiz_id;
    page_num = Number($("#page_num").val());
    total_num = Number($("#total_num").val());
    last = Number($("#last").val());
    required = Number($("#required").val());
    typesetting = Number($("#typesetting").val());
    step = Number($("#current_page").html());
    total_time = Number($("#total_time").html());
    status = 0;
    get_page(page_num);
    $("#footer").hide();
    $("#finished").click(next_page);
    $.extend($.validator.messages, {required: "该题必须作答"});
    csrftoken = getCookie('csrftoken');       
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
      }
    });
});

var min,sec;

function initTime(){
    min = Number($("#time").attr("value"));
    sec = 0;
    setInterval('countTime()',1000);
}

var flag = 5;

function flash(text,time)
{
    $("#loading_text").html(text);
    $("#loading_div2").css('display','block');
    if(time!=0)setTimeout(function(){
        $("#loading_div2").css('display','none');
    },time);
}

function connect(){
    $.ajax({
    url: url + "/check_in/",
    type: 'get',
    success: function(data){
        if(data.msg == 'timeup')
        {        
            flash("测验已结束，自动为您交卷", 0);
            $("#tosubmit").attr("disabled",true).attr("title","正在交卷"); 
            save_answers(
                function(d){
                    location.href = url + "/submit/";      
                }, 0);
        }
        if(data.msg == 'finished')
        {
            window.location = '/frontend/index/';
            return;
        }
        if(data.msg == "reconnect")
        {
            last = data.msg;
        }
        else if(data.msg == 'error')
        {
            alert('服务器发生错误，请联系管理员');
        }
    },
    error: function(){
        flag--;
        if(flag == 0)
        {
            flag = 10;
            if ((navigator.userAgent.indexOf('MSIE') >= 0) 
            && (navigator.userAgent.indexOf('Opera') < 0)){
            if(confirm('与服务器断开连接，是否重新连接？'))
                connect();
            }
            else $.confirm({
                confirmButtonClass: 'btn-info',
                cancelButtonClass: 'btn-default',
                keyboardEnabled: true,
                title: '警告',
                content: '与服务器断开连接，是否重新连接？',
                confirmButton:'是',
                cancelButton:'否',
                closeIcon:true,
                confirm: function(){
                    connect();
                }
            });
        }
        else
        {
            connect();
        }
    }
    });
}

function countTime(){
    if(min >= total_time)
    {
        clearInterval();
        return;
    }
    if(sec == 60) {
        min++;
        sec = 0;
        connect();
        if(min >= total_time){
            flash("测验已结束，自动为您交卷", 0);
            $("#tosubmit").attr("disabled",true).attr("title","正在交卷");
            save_answers(
                function(d){
                    location.href = url + "/submit/";     
                }, 0);
            clearInterval();
        }
    }
    $("#time").text(min + ":" + sec);
    sec++;
}

function jump(){
    $("#time").focus();
    jump_page = Number($("#enter_page").val());
    jump(jump_page);
}

function jump(jump_page){
    if(jump_page == page_num)return;
    if(jump_page < 1 || jump_page > total_num)flash("超出范围", 2000);
    else{
        if(jump_page > page_num){
            if(!check_required()){
                flash("必须全部作答完才能继续", 2000);
                return;
            }
            if(category == 1 && check()){
                flash("各项分值之和不等于总分值！", 2000);
                return;
            }
            if(required == 1 && jump_page > step + 1){
                flash("必须依次作答", 2000);
                jump_page = step + 1;
            }
        } 
        get_page(jump_page);
    }
}

function check_required(){
    if(required == 1){
        value = $("#form").valid();
        return value;
    }
    return true;
}

function next_page(){
    if(!check_required()){
        flash("必须全部作答完才能继续", 2000);
        return;
    }
    if(category == 1 && check()){
        flash("各项分值之和不等于总分值！", 2000);
        return;
    }
    if(page_num < total_num)get_page(page_num + 1);
    else if(status == 1)save_answers(function(){
        if ((navigator.userAgent.indexOf('MSIE') >= 0) 
            && (navigator.userAgent.indexOf('Opera') < 0)){
            if(confirm('测验到此结束，是否交卷？'))
                submit();
        }
        else $.confirm({
                confirmButtonClass: 'btn-info',
                cancelButtonClass: 'btn-default',

                keyboardEnabled: true,
                title: '提示',
                content: '测验到此结束，是否交卷？',
                confirmButton:'交卷',
                cancelButton:'继续作答',
                closeIcon:true,
                confirm: function(){
                    submit();
                }
            });
    },0);
}

function prev_page(){
    if(category == 1 && check()){
        flash("各项分值之和不等于总分值！", 2000);
        return;
    }
    if(page_num > 1)get_page(page_num - 1);
}

function to_submit(){
    $("#tosubmit").attr("disabled",true).attr("title","正在交卷");
    $('#loading_div').css('display','block');
    location.href = url + "/submit/";
}

function submit2(d)
{   
    flash('正在检查作答情况，请耐心等待',0);
    $.ajax({
        url: url + "/check_answer/",
        type: 'get',
        success: function(data){
            $('#loading_div2').css('display','none');
            if(data.msg == 0){
                if ((navigator.userAgent.indexOf('MSIE') >= 0) 
                    && (navigator.userAgent.indexOf('Opera') < 0)){
                    if(confirm('确定要提交吗？'))to_submit();
                }
                else $.confirm({
                    confirmButtonClass: 'btn-info',
                    cancelButtonClass: 'btn-default',
                    keyboardEnabled: true,
                    title: '提示',
                    content: '确定要提交吗？',
                    confirmButton:'确定',
                    cancelButton:'取消',
                    closeIcon:true,
                    confirm: function(){
                        to_submit();
                    }
                });
            }
            else{
                get_page(data.msg); 
                if ((navigator.userAgent.indexOf('MSIE') >= 0) 
                    && (navigator.userAgent.indexOf('Opera') < 0)){
                    if(confirm('还有题目未作答，确定要提交吗？'))
                        to_submit();
                }
                else $.confirm({
                    confirmButtonClass: 'btn-info',
                    cancelButtonClass: 'btn-default',
                    keyboardEnabled: true,
                    title: '警告',
                    content: '还有题目未作答，确定要提交吗？',
                    confirmButton:'确定',
                    cancelButton:'继续作答',
                    closeIcon:true,
                    confirm: function(){
                        to_submit();
                    }
                });
            }
        },
        error: function(){
            $('#loading_div2').css('display','none');
            alert('error');
        }
    });
}

function submit(){
    if(!check_required()){
        flash("必须全部作答完才能继续", 2000);
        return;
    }
    if(category == 1 && check()){
        flash("各项分值之和不等于总分值！", 2000);
        return;
    }
    if(status == 1)save_answers(submit2,0);
    else submit2(0);
}

function check(){
    value = 0;
    $.each(answer, function(i,e){
        value += Number(e);
    });
    return (value != score);
}

function save_answers(done, args){
    $.ajax({
        url: url + "/response/",
        type: 'post',
        data: {
            page: page_num,
            answer: JSON.stringify(answer)
        },
        success: function(data){
            if(data.error == 'finished'){
                window.location = '/frontend/index/';
                return;
            }
            step = data.current_page - 1;
            $("#current_page").html(step);
            done(args);
        },
        error: function(){
            alert('error');
        }
    });
    return false;
}

function change_answer(obj){
    if(category == 4){
        for(var i in answer){
            if(answer[i] == obj.name.split('_')[1]){
                answer[i] = 3;
                $("input[name='answer_" + answer[i] + "'][value=" + (i+1) + "]").attr("checked",false);
            }
        }
        $("input[name='answer_" +  answer[obj.value-1] + "'][value=" + obj.value + "]").attr("checked",false);
        answer[obj.value-1] = Number(obj.name.split('_')[1]);
        if(answer.length == 2){
            answer[2-obj.value] = 6 - answer[obj.value-1];
            $("input[name='answer_" + answer[2-obj.value] + "'][value=" + (3-obj.value) + "]").click();
        }
    }
    else{
        answer[obj.name.split('_')[1]-1] = obj.value;
    }
    status = 1; 
    $("label.invalid").hide(); 
}

function get_page2(page){
    if(page < last){
        flash("无法修改断开连接前的答卷", 2000);
        if(last > total_num){
            flash("您已答完全部问题，自动为您交卷", 0);
            $("#tosubmit").attr("disabled",true).attr("title","正在交卷");
            location.href = url + "/submit/";     
        }
        return;
    }
    clear();
    $("#stem_des").html("正在加载题目，请耐心等候...");
    $('#loading_div').css('display','block');
    $.ajax({
        url: url + "/response/",
        type: 'get',
        data: {
            page: page
        },
        success: function(data){
            if(data.error == 'timeup'){
                flash("测验已结束，自动为您交卷", 0);
                $("#tosubmit").attr("disabled",true).attr("title","正在交卷");
                location.href = url + "/submit/";     
                return;
            }
            if(data.error == 'finished'){
                window.location = '/frontend/index/';
                return;
            }
            clear();
            page_num = page;
            $("#page_num").val(page_num);
            load_questions(data);
            if(page_num == total_num)$('#finished').show();
            else $("#finished").hide();
            finished
            $('#loading_div').css('display','none');
        },
        error: function(){
            clear();
            $("#stem_des").html("<a id='refresh' href='#'>加载题目失败，点击重试。</a>");
            $('#loading_div').css('display','none');
            $("#refresh").click(function(){
                get_page(page);
            });        }
    });
}

function get_page(page){
    $("#time").focus();
    if(status == 1)save_answers(get_page2, page);
    else get_page2(page);
}

function clear(){
    $("#stem_des").html("");
    $("#question_list").html("");
}

function freshbar(){
    if(page_num == 1) $("#tofirst").attr("disabled",true).attr("title","当前已经是第一页");
    else if(last>1) $("#tofirst").attr("disabled",true).attr("title","无法修改断开连接前的答卷");
    else $("#tofirst").attr("disabled",false).attr("title","");
    if(page_num == 1) $("#toprev").attr("disabled",true).attr("title","当前已经是第一页");
    else if(last>=page_num) $("#toprev").attr("disabled",true).attr("title","无法修改断开连接前的答卷");
    else $("#toprev").attr("disabled",false).attr("title","");
    if(page_num == total_num) $("#tolast").attr("disabled",true).attr("title","当前已经是最后一页");
    else if(required && step < total_num-1) $("#tolast").attr("disabled",true).attr("title","必须依次作答");
    else $("#tolast").attr("disabled",false).attr("title","");
    if(page_num == total_num) $("#tonext").attr("disabled",true).attr("title","当前已经是最后一页");
    else $("#tonext").attr("disabled",false).attr("title","");
    if(required && step < total_num && page_num != total_num) $("#tosubmit").attr("disabled",true).attr("title","作答完全部题目才可交卷");
    else $("#tosubmit").attr("disabled",false).attr("title","");
}

function load_questions(data){
    freshbar();
    category = data.page.category;
    var description = data.page.description;
    var ques_list = data.page.questions;
    answer = data.answer;
    if(answer == null){
        answer = [];
        if(category == 4)$(ques_list).each(function(){
            answer.push(3);
        });
        else $(ques_list).each(function(index, element){
            if(element.category==1)answer.push(-1);
            else if(element.category==3)answer.push(0);
            else answer.push('');
        });
    }

    if(category == 3)$("#stem").hide();
    else if(category == 1){
        score = data.page.score;
        $("#stem_des").append("<h3>第" + page_num + "题&nbsp;&nbsp;&nbsp;&nbsp;<small>共"+score+"分</small></h3>");
        $("#stem_des").append("<h5>"+description+"</h5>");
        $("#stem").show();
        status = 1;
    }
    else{
        $("#stem_des").append("<h3>第" + page_num + "题</h3>");
        $("#stem_des").append("<h5>"+description+"</h5>");
        $("#stem").show();
    } 
    if(category == 4){
        $(ques_list).each(function(index,element){
            $("#question_list").append("<div class=\"row\">" +
         "<div class=\"page-header col-xs-12\" style=\"margin-top:2px;\">" +
         "<div class=\"row\"><div class=\"col-xs-1\" style=\"margin-top:-5px;text-align:right;\"><h5>" +
         page_num+"."+(index+1) + "</h5></div><div class=\"col-xs-9\" style=\"margin-top:2px;text-align:left;padding-left:0px;\">" + element.description +
         "</div><div class=\"col-xs-2\" id=\"option_list_select_" + (index+1) + "\" style=\"margin-top:2px;text-align:left;margin-left:0px;\"></div>"+
         "<div class=\"col-xs-12\" id=\"option_list_"+(index+1)+"\" style=\"margin-top:2px;text-align:left;margin-left:0px;padding-left:0px;padding-right:0px;\">" +
                "</div></div></div></div>");
            if(typesetting == 1){
                $("#option_list_"+(index+1)).append("<div class=\"col-xs-1\"></div><div class=\"radio col-xs-11\" style=\"margin-top:2px;text-align:left;padding-left:0px;\">"+
                    "<label><input type=\"radio\" name=\"answer_5\" value=\"" + (index+1) + "\" onchange=\"change_answer(this)\">最符合</input></label>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"+
                    "<label><input type=\"radio\" name=\"answer_1\" value=\"" + (index+1) + "\" onchange=\"change_answer(this)\">最不符合</input></label></div>");       
            }
            else{
                $("#option_list_"+(index+1)).append("<div class=\"col-xs-1\"></div><div class=\"radio col-xs-11\" style=\"margin-top:2px;text-align:left;padding-left:0px;\">"+
                    "<label><input type=\"radio\" name=\"answer_5\" value=\"" + (index+1) + "\" onchange=\"change_answer(this)\">最符合</input></label></div>");
                $("#option_list_"+(index+1)).append("<div class=\"col-xs-1\"></div><div class=\"radio col-xs-11\" style=\"margin-top:2px;text-align:left;padding-left:0px;\">"+
                    "<label><input type=\"radio\" name=\"answer_1\" value=\"" + (index+1) + "\" onchange=\"change_answer(this)\">最不符合</input></label></div>");
            }
            if(answer[index])$("input[name='answer_" + answer[index] + "'][value=" + (index+1) + "]").attr("checked",true);
        });
    }
    else $(ques_list).each(function(index,element){
        $("#question_list").append("<div class=\"row\">" +
         "<div class=\"page-header col-xs-12\" style=\"margin-top:2px;\">" +
         "<div class=\"row\"><div class=\"col-xs-1\" style=\"margin-top:-5px;text-align:right;\"><h5>" +
         page_num+"."+(index+1) + "</h5></div><div class=\"col-xs-9\" style=\"margin-top:2px;text-align:left;padding-left:0px;\">" + element.description +
         "</div><div class=\"col-xs-2\" id=\"option_list_select_" + (index+1) + "\" style=\"margin-top:2px;text-align:left;margin-left:0px;\"></div>"+
         "<br /><div class=\"col-xs-12 radio\" id=\"option_list_"+(index+1)+"\" style=\"text-align:left;padding-left:0px;padding-right:0px;overflow-x:auto;width:100%;white-space:nowrap;\" >" +
            "<div class=\"col-xs-1\"></div></div></div></div></div>");
        if(element.category == 1){
            var option_list = element.options;
            $(option_list).each(function(i,e){
                if(typesetting == 1){
                    $("#option_list_"+(index+1)).append("<label><input type=\"radio\" name=\"answer_"
                        + (index+1) + "\" value=\"" + (i+1) + "\" onchange=\"change_answer(this)\">" + e.description + "</input></label>"+
                        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
                }
                else{
                    if(i==0){
                    $("#option_list_"+(index+1)).append("<div class=\"radio col-xs-11\" style=\"text-align:left;margin-left:0px;padding-left:0px;\">"+
                    "<label><input type=\"radio\" name=\"answer_" + (index+1) + "\" value=\"" + (i+1) + "\" onchange=\"change_answer(this)\">" + e.description + "</input></label></div>");}
                    else
                    {
                        $("#option_list_"+(index+1)).append("<div class=\"col-xs-1\"></div><div class=\"radio col-xs-11\" style=\"text-align:left;margin-left:0px;padding-left:0px;\">"+
                    "<label><input type=\"radio\" name=\"answer_" + (index+1) + "\" value=\"" + (i+1) + "\" onchange=\"change_answer(this)\">" + e.description + "</input></label></div>");
                    }
                }
               });
            if(answer[index])$("input[name='answer_" + (index+1) + "'][value=" + answer[index] + "]").attr("checked",true);
        }
        else if (element.category == 2){
            $("#option_list_"+(index+1)).append("<div class=\"col-xs-10 col-xs-offset-1\" style=\"margin-top:3px;\">" +
                    "<textarea name=\"answer_" + (index+1) + "\" class=\"form-control\" rows=\"5\" onchange=\"change_answer(this)\"></textarea><br></div>");
            if(answer[index])$("textarea[name='answer_" + (index+1) + "']").val(answer[index]);
        }
        else if (element.category == 3){
            if(typesetting == 1){
                select = $("<select></select>").attr('name','answer_'+(index+1)).attr('class','form-control select').attr('onchange','change_answer(this)').attr('style','width:100%');
                select.append("<option value='0'>0</option>");
                for(i=1;i<=score;i++)
                    select.append("<option value='"+i+"'>"+i+"</option>");
                div = $("<div class=\"col-sm-12 col-xs-12\" style=\"margin-left:0px;margin-right:0px;padding-left:0px;padding-right:0px;\"></div>");
                child = $("<div class=\"choose_box col-xs-12\" style=\"text-align:center;\"></div>");
                child.append(select);
                div.append(child);
                $("#option_list_select_"+(index+1)).append(div);
                $("select[name='answer_" + (index+1) + "']").val(answer[index]);
            }
            else{
                for(i=0;i<=score;i++){
                    $("#option_list_"+(index+1)).append("<label><input type=\"radio\" name=\"answer_"
                        + (index+1) + "\" value=\"" + i + "\" onchange=\"change_answer(this)\">" + i + "分</input></label>"+
                        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
                }
                if(answer[index])$("input[name='answer_" + (index+1) + "'][value=" + answer[index] + "]").attr("checked",true);
                else $("input[name='answer_" + (index+1) + "'][value=0]").attr("checked",true);
            }
        }
    });
    if(required){
        $("[name^='answer']").attr("required","true");
        $("#form").validate({
            errorClass: "invalid",
            errorPlacement:function(error,element){
                err_pos = element.parents("div[id^='option_list']").parent().parent();
                if(err_pos.children(".invalid").length==0)
                err_pos.prepend(error);
            }
        });
    }
    status = 0;
}
