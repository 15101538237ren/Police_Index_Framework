var category, typesetting, score, required;
var _category = ["","单选题","简答题","赋分题"];
var answer = [];

$(function(){
    typesetting = Number($("#typesetting").val());
    data = JSON.parse($("#page").val());
    required = Number($("#required").val());
    load_questions(data);
});

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
    }
    else{
        answer[obj.name.split('_')[1]-1] = obj.value;
    }
}

function check_required(){
    if(required == 1){
        value = $("#form").valid();
        return value;
    }
    return true;
}

function check(){
    value = 0;
    $("select").each(function(i,e){
        value += Number(e.value);
    });
    return (value != score);
}

function flash(text,time)
{
    $("#loading_text").html(text);
    $("#loading_div2").css('display','block');
    if(time!=0)setTimeout(function(){
        $("#loading_div2").css('display','none');
    },time);
}

function submit(){
    if(!check_required()){
        flash("必须全部作答完才能继续", 2000);
        return false;
    }
    if(category == 1 && check()){
        flash("各项分值之和不等于总分值！", 2000);
        return false;
    }
    return true;
}

function load_questions(data){
    category = data.category;
    var description = data.description;
    var ques_list = data.questions;

    if(category == 3)$("#stem").hide();
    else if(category == 1){
        score = data.score;
        $("#stem_des").append("<h3>例题&nbsp;&nbsp;&nbsp;&nbsp;<small>共"+score+"分</small></h3>");
        $("#stem_des").append("<h5>"+description+"</h5>");       
        $("#stem").show();
    }
    else{
        $("#stem_des").append("<h3>例题</h3>");
        $("#stem_des").append("<h5>"+description+"</h5>");
        $("#stem").show();
    }
    if(category == 4){
        $(ques_list).each(function(index,element){
            $("#question_list").append("<div class=\"row\">" +
         "<div class=\"page-header col-lg-10 col-lg-offset-1 col-md-10 col-md-offset-1 col-sm-12 col-xs-12\" style=\"margin-top:2px;\">" +
         "<div class=\"row\"><div class=\"col-sm-2 col-xs-2\" style=\"margin-top:-5px;text-align:center;\"><h5>" +
         (index+1) + "</h5></div><div class=\"col-sm-8 col-xs-8\" style=\"margin-top:3px;text-align:left;\">" + element.description + 
         "</div><div class=\"col-sm-2 col-xs-2\" id=\"option_list_select_" + (index+1) + "\" style=\"margin-top:0px;\"></div>"+
         "<div class=\"col-sm-10 col-sm-offset-2 col-xs-12\" id=\"option_list_"+(index+1)+"\" style=\"margin-top:2px;\"></div></div></div></div>");
            if(typesetting == 1){
                $("#option_list_"+(index+1)).append("<div class=\"radio col-sm-3 col-sm-offset-0 col-xs-12 col-xs-offset-0\" style=\"margin-top:2px;\">"+
                    "<label><input type=\"radio\" name=\"answer_5\" value=\"" + (index+1) + "\" onchange=\"change_answer(this)\">最符合</input></label></div>");
                $("#option_list_"+(index+1)).append("<div class=\"radio col-sm-3 col-sm-offset-0 col-xs-12 col-xs-offset-0\" style=\"margin-top:3px;\">"+
                    "<label><input type=\"radio\" name=\"answer_1\" value=\"" + (index+1) + "\" onchange=\"change_answer(this)\">最不符合</input></label></div>");       
            }
            else{
                $("#option_list_"+(index+1)).append("<div class=\"radio col-sm-12 col-sm-offset-0 col-xs-12 col-xs-offset-0\">"+
                    "<label><input type=\"radio\" name=\"answer_5\" value=\"" + (index+1) + "\" onchange=\"change_answer(this)\">最符合</input></label></div>");
                $("#option_list_"+(index+1)).append("<div class=\"radio col-sm-12 col-sm-offset-0 col-xs-12 col-xs-offset-0\">"+
                    "<label><input type=\"radio\" name=\"answer_1\" value=\"" + (index+1) + "\" onchange=\"change_answer(this)\">最不符合</input></label></div>");
            }
        });
    }
    else $(ques_list).each(function(index,element){
        $("#question_list").append("<div class=\"row\">" +
         "<div class=\"page-header col-lg-10 col-lg-offset-1 col-md-10 col-md-offset-1 col-sm-12 col-xs-12\" style=\"margin-top:3px;\">" +
         "<div class=\"row\"><div class=\"col-sm-2 col-xs-2\" style=\"margin-top:-5px;text-align:right;\"><h5>" +
         (index+1) + "<small>(" + _category[element.category] + ")</small></h5></div><div class=\"col-sm-8 col-xs-8\" style=\"margin-top:3px;text-align:left;\">" + element.description + 
         "</div><div class=\"col-sm-2 col-xs-2\" id=\"option_list_select_" + (index+1) + "\" style=\"margin-top:0px;\"></div>"+
         "<div class=\"col-sm-10 col-sm-offset-2 col-xs-12\" id=\"option_list_"+(index+1)+"\" style=\"margin-top:3px;\"></div></div></div>");
        if(element.category == 1){
            var option_list = element.options;
            $(option_list).each(function(i,e){
                if(typesetting == 1){
                    $("#option_list_"+(index+1)).append("<div class=\"radio col-sm-3 col-sm-offset-0 col-xs-3 col-xs-offset-0\"  style=\"margin-top:3px;margin-right:0px;margin-left:0px;\">"+
                    "<label style=\"margin-right:0px;margin-left:0px;padding-right:0px;padding-left:0px;\"><input type=\"radio\" name=\"answer_" + (index+1) + "\" value=\"" + (i+1) + "\" onchange=\"change_answer(this)\">" + e.description + "</input></label></div>"); 
                }
                else{
                     $("#option_list_"+(index+1)).append("<div class=\"radio col-sm-12 col-sm-offset-0 col-xs-10 col-xs-offset-0\">"+
                    "<label><input type=\"radio\" name=\"answer_" + (index+1) + "\" value=\"" + (i+1) + "\" onchange=\"change_answer(this)\">" + e.description + "</input></label></div>");
                 }
               });
        }
        else if (element.category == 2){
            $("#option_list_"+(index+1)).append("<div class=\"col-sm-10 col-sm-offset-0 col-xs-10 col-xs-offset-0\" style=\"margin-top:3px;\">" +
                    "<textarea name=\"answer_" + (index+1) + "\" class=\"form-control\" rows=\"5\" onchange=\"change_answer(this)\"></textarea><br></div>");
        }
        else if (element.category == 3){
            select = $("<select></select>").attr('name','answer_'+(index+1)).attr('class','form-control select').attr('onchange','change_answer(this)').attr('style','width:100%');
            select.append("<option value='0'>0</option>");
            for(i=1;i<=score;i++)
                select.append("<option value='"+i+"'>"+i+"</option>");
            div = $("<div class=\"col-sm-12 col-xs-12\" style=\"margin-left:0px;margin-right:0px;padding-left:0px;padding-right:0px;\"></div>");
            child = $("<div class=\"choose_box col-sm-12 col-xs-12\" style=\"margin-left:0px;margin-right:0px;padding-left:0px;padding-right:0px;\"></div>");
            child.append(select);
            div.append(child);
            $("#option_list_select_"+(index+1)).append(div);
        }
    });
    if(required){
        $("[name^='answer']").attr("required","true");
        $("#form").validate({
            errorClass: "invalid",
            errorPlacement:function(error,element){
                //error.appendTo(element.parents("div[id^='option_list']").parent().prev().children());
            }
        });
    }
}