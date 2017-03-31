var template_str;
var template = {};

var WIDTH = 595,HEIGHT=842; 
$(function(){
    csrftoken = getCookie('csrftoken');       
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
      }
    });
});

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


function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(function(){
    template_str = $("#template_str").val();
    template = JSON.parse(template_str);
    init();
    $(".editable").attr("title","编辑");
    $(".add").click(add);
    $(".edit").click(edit);
    $(".submit").click(Submit);
    $(window).scroll(nav).scroll();
    $(".pick-a-color").pickAColor();
    $("#Select3").change(function(){
        if($(this).children('option:selected').val() == 0)
            $("#evaluation_attr").hide();
        else $("#evaluation_attr").show();
    });
});

function nav(){
    $(".page").each(function(){
        start = $(this).offset().top;
        end = $(this).height() + start;
        loc = $(window).scrollTop() + 150;
        if(start <= loc && loc < end){
            id = $(this).attr("id");
            $("li.active").removeClass("active");
            $("a[href='#" + id + "']").parent().attr("class","active");
            if(id == 'page_cover'){
                $("#index").val('cover');
            }
            else{
                $("#index").val(id.split('_')[1]);
            }
        }
    });
}

function edit(){
    id = $(this).attr("id");
    index = id.split('_')[1];
    order = id.split('_')[3];
    $("#order").val(order);
    $("#description_style").hide();
    $("#description_line_div").hide();
    if(order == 'header' || order == 'footer'){
        $("#index").val(index);
        if(index == 'cover')element = template.cover[order];
        else element = template[order];
        if(order == 'header')$("#description_label").html("编辑页眉");
        else $("#description_label").html("编辑页脚");
        $("#description_content").val(element.content).show();
        $("#description_size").val(element.size);
        $("#description_color").val(element.color);
        $(".current-color").css("background-color","#"+element.color);
        update_select("description_font", select_options.font_type, element.font);
        update_select("description_align", select_options.align, element.align);
        if(order == 'header'){
            update_select('description_style', {'info':'自动生成','text':'输入'}, element.style);
            if(element.style == 'info')$("#description_content").hide();
            $("#description_style").change(function(){
                if($(this).children('option:selected').val() == 'info')
                    $("#description_content").hide();
                else $("#description_content").show();
            });
            $("#description_style").show();
            $("#description_line_div").show();
            if(element.line)$("#description_line").attr("checked", "true");
        }
        $("#description").modal('show');
        return;
    }
    if(order == 'pagination'){
        $("#" + order + "_size").val(template.pagination.size);
        update_select(order + "_align", select_options.align, template.pagination.align);
        $("#" + order + "_color").val(template.pagination.color);
        $(".current-color").css("background-color","#"+template.pagination.color);
        $("#" + order).modal('show');
        return;
    }
    if(order == 'margin'){
        index = $("#index").val();
        if(index == 'cover')element = template.cover.margin;
        else element = template.margin;
        $("#margin_left").val(element.left);
        $("#margin_right").val(element.right);
        $("#margin_top").val(element.top);
        $("#margin_bottom").val(element.bottom);
        $("#margin").modal('show');
        return;
    }
    if(order == 'background'){
        index = $("#index").val();
        if(index == 'cover')element = template.cover.background;
        else element = template.background;
        if(element){
            $("[data-dz-thumbnail]").attr("src","/static/imgs/" + element).attr("width","120px").attr("height","120px");
            $("#image_src").val(element);
        }
        else{
            $("[data-dz-thumbnail]").attr("src","/static/imgs/add.jpg").attr("width","120px").attr("height","120px");
            $("#image_src").val('');
        }
        $("#image_size").hide();
        $("#delete_background").show();
        $("#image").modal('show');
        return;
    }
    $("#index").val(index);
    if(index == 'cover')element = template.cover.body[order];
    else element = template.body[index][order];
    switch(element.style){
        case 'description':
            $("#description_label").html("编辑文字说明");
            $("#description_content").val(element.content).show();
            $("#description_size").val(element.size);
            $("#description_color").val(element.color);
            $(".current-color").css("background-color","#"+element.color);
            update_select('description_font', select_options.font_type, element.font);
            update_select('description_align', select_options.align, element.align);
            break;
        case 'image':
            $("[data-dz-thumbnail]").attr("src","/static/imgs/" + element.src).attr("width","120px").attr("height","120px");
            $("#image_src").val(element.src);
            $("#width").val(element.width);
            $("#height").val(element.height);
            update_select('image_align', select_options.align, element.align);
            $("#image_size").show();
            $("#delete_background").hide();
            break;
        case 'chart':
            update_select('chart_type', select_options.chart_type, element.type);
            update_select('chart_way', select_options.chart_way, element.way);
            update_select('chart_align', select_options.align, element.align);
            update_select('chart_score', {'percent':'百分比','normal':'标准分'}, element.score);
            $("#chart_title").val(element.title);
            $("#chart_color").val(element.color);
            $("#chart_width").val(element.width);
            $("#chart_height").val(element.height);
            $(".current-color").css("background-color","#"+element.color);
            update_chart(element.dimensions, element.norm_line);
            break;
        case 'dimension':
            $("#title_content").val(element.content);
            $("#title_size").val(element.title_size);
            $("#title_color").val(element.title_color);
            $("#evaluation_size").val(element.size);
            $("#evaluation_color").val(element.color);
            $("#title_color").parent().children(".current-color").css("background-color","#"+element.title_color);
            $("#evaluation_color").parent().children(".current-color").css("background-color","#"+element.color);
            update_select('title_font', select_options.font_type, element.title_font);
            update_select('evaluation_font', select_options.font_type, element.font);
            config = [element.id,element.type,element.evaluation];
            update_dimension_select(config);
            if(element.evaluation)$("#evaluation_attr").show()
            else $("#evaluation_attr").hide();
            break;
        case 'info':
            $("#info_size").val(element.size);
            $("#info_content").val(element.content);
            $("#info_color").val(element.color);
            $(".current-color").css("background-color","#"+element.color);
            update_select('info_attr', select_options.info, element.attr);
            update_select('info_font', select_options.font_type, element.font);
            update_select('info_align', select_options.align, element.align);
            break;
    }
    $("#" + element.style).modal('show');
}

function add(){
    style = $(this).val();
    index = $("#index").val();
    if(style == 'page'){
        template.body.push([]);
        save();
        update_pages();
        return;
    }
    if(style == 'line'){
        if(index == 'cover')template.cover.body.push({style:'line'});
        else template.body[Number(index)].push({style:'line'});
        save();
        update_pages();
        return;
    }
    if(style == 'blank'){
        if(index == 'cover')template.cover.body.push({style:'blank'});
        else template.body[Number(index)].push({style:'blank'});
        save();
        update_pages();
        return;
    }
    $("#order").val(-1);
    $("[data-dz-thumbnail]").attr("src","/static/imgs/add.jpg").attr("width","120px").attr("height","120px");
    $("#width").val(320);
    $("#height").val(240);
    $("#chart_width").val(320);
    $("#chart_height").val(240);
    $("#image_src").val('add.jpg');
    $("#image_size").show();
    $("#delete_background").hide();
    $("#description_label").html("编辑文字说明");
    $("#description_content").val("").show();
    $("#description_style").hide();
    $("#description_line_div").hide();
    $("#description_size").val(20);
    $("#info_size").val(20);
    $("#title_size").val(25);
    $("#evaluation_size").val(20);
    $("#chart_title").val("");
    $(".pick-a-color").val("000000");
    $(".current-color").css("background-color","#000000");
    update_chart([], []);
    $("#"+style).modal('show');
}

function Delete(){
    id = $(this).parent().parent().attr("id");
    index = id.split('_')[1];
    order = Number(id.split('_')[3]);
    if(index == 'cover')template.cover.body.splice(order, 1);
    else template.body[Number(index)].splice(order, 1);
    save();
    update_pages();  
}

function up(){
    id = $(this).parent().parent().attr("id");
    index = id.split('_')[1];
    order = Number(id.split('_')[3]);
    if(order <= 0)return;
    if(index == 'cover')element = template.cover.body;
    else element = template.body[Number(index)];
    temp = element[order];
    element[order] = element[order-1];
    element[order-1] = temp;
    save();
    update_pages();
}

function down(){
    id = $(this).parent().parent().attr("id");
    index = id.split('_')[1];
    order = Number(id.split('_')[3]);
    if(index == 'cover')element = template.cover.body;
    else element = template.body[Number(index)];
    if(order >= element.length - 1)return;
    temp = element[order];
    element[order] = element[order+1];
    element[order+1] = temp;
    save();
    update_pages();
}

function Delete_page(){
    index = $("#index").val();
    if(index=='cover')return;
    if(!confirm('操作无法撤销，确定删除该页吗？'))return;
    template.body.splice(Number(index),1);
    save();
    update_pages();
}

function Up_page(){
    index = $("#index").val();
    if(index=='cover' || Number(index)<=0)return;
    index = Number(index);
    temp = template.body[index];
    template.body[index] = template.body[index-1];
    template.body[index-1] = temp;
    save();
    update_pages();
}

function Down_page(){
    index = $("#index").val();
    if(index=='cover' || Number(index) >= template.body.length-1)return;
    index = Number(index);
    temp = template.body[index];
    template.body[index] = template.body[index+1];
    template.body[index+1] = temp;
    save();
    update_pages();
}

function init(){
    update_pages();
    update_dimension_select([]);
    update_select('chart_type', select_options.chart_type, null);
    update_select('description_font', select_options.font_type, null);
    update_select('info_font', select_options.font_type, null);
    update_select('title_font', select_options.font_type, null);
    update_select('evaluation_font', select_options.font_type, null);
    update_select('norm_line', select_options.norm_line, null);
    update_select('chart_way', select_options.chart_way, null);
    update_select('image_align', select_options.align, null);
    update_select('description_align', select_options.align, null);
    update_select('info_align', select_options.align, null);
    update_select('pagination_align', select_options.align, null);
    update_select('chart_align', select_options.align, 'center');
    update_select('info_attr', select_options.info, null);
    $("#info_attr").change(function(){
        $("#info_content").val(select_options.info[$(this).val()] + "：");
    });
    $("#delete_background").click(function(){
        index = $("#index").val();
        if(index == 'cover')template.cover.background = null;
        else template.background = null;
        save();
        update_pages();
    });
    init_chart_dimensions();
}

function init_chart_dimensions(){
    var leftSel = $("#all_dimensions"); 
    var rightSel = $("#chart_dimensions");
    $("#toright").click(function(){
        leftSel.find("option:selected").each(function(){ 
            $(this).remove().appendTo(rightSel); 
        }); 
    });
    $("#toleft").click(function(){         
        rightSel.find("option:selected").each(function(){ 
            $(this).remove().appendTo(leftSel); 
        }); 
    }); 
    $("#toup").click(function(){
        var SelOpt = rightSel.find("option:selected");
        if(SelOpt.length==1&&SelOpt.prev())SelOpt.prev().before(SelOpt);
    });
    $("#todown").click(function(){         
        var SelOpt = rightSel.find("option:selected");
        if(SelOpt.length==1&&SelOpt.next())SelOpt.next().after(SelOpt);
    }); 
    leftSel.dblclick(function(){ 
        $(this).find("option:selected").each(function(){ 
            $(this).remove().appendTo(rightSel); 
        }); 
    }); 
    rightSel.dblclick(function(){ 
        $(this).find("option:selected").each(function(){ 
            $(this).remove().appendTo(leftSel); 
        }); 
    }); 
}

function update_dimension_select(config){
    var v1=config[0]?config[0]:null;
    var v2=config[1]?config[1]:null;
    var v3=config[2]?config[2]:null;
    update_select("Select1", select_options.dimensions, v1);
    update_select("Select2", select_options.type, v2);
    update_select("Select3", select_options.evaluation, v3);
}

function update_select(id, object, selected){
    var $s = $("#" + id);
    $s.html("");
    $.each(object,function(k,v){
        var $opt=$("<option>").text(v).val(k);
        if(k==selected)$opt.attr("selected", "selected");
        $opt.appendTo($s);    
    }); 
}

function update_cover(){
    if(template.cover == null)template.cover = {
        header: {'content':'页眉','font':'SimSun','size':15,'align':'right','color':'000000','style':'info'},
        footer: {'content':'页脚','font':'SimSun','size':15,'align':'center','color':'000000'},
        margin: {'left':35,'right':35,'top':35,'bottom':35},
        body:[],
    };
    update_page('cover',template.cover.body);
}

function update_pages(){
    $("#nav").html("");
    $("#list").html("");
    if(template.header == null)template.header = {'content':'页眉','font':'SimSun','size':15,'align':'right','color':'000000','style':'info'};
    if(template.footer == null)template.footer = {'content':'页脚','font':'SimSun','size':15,'align':'center','color':'000000'};
    if(template.pagination == null)template.pagination = {'size':15,'align':'right','color':'000000'};
    if(template.margin == null)template.margin = {'left':35,'right':35,'top':35,'bottom':35};
    if(template.body == null)template.body = [];
    update_cover();                 
    $(template.body).each(update_page);
    $(window).scroll();
}

function update_page(index,element){
    page = $("<div></div>").attr("id", "page_" + index).attr("class", "page");
    if(index == 'cover'){
        header = template.cover.header;
        footer = template.cover.footer;
        if(template.cover.background)page.css('background-image',"url(/static/imgs/"+template.cover.background+")");
        margin = template.cover.margin;
    }
    else{
        header = template.header;
        footer = template.footer;
        if(template.background)page.css('background-image',"url(/static/imgs/"+template.background+")");
        margin = template.margin;
    }
    content = $("<div></div>").attr("class","content").css({'margin-left':margin.left,'margin-right':margin.right,'width': WIDTH-margin.left-margin.right,'height':HEIGHT-margin.top-margin.bottom});
    header_div = $("<div></div>").attr("id","page_" + index + "_item_header").addClass("editable").css({'margin-left':margin.left,'margin-right':margin.right,"height":margin.top}).click(edit);
    header_content = header.content.replace(/ /g,"&nbsp;");
    if(header.style == 'info')header_content = '测验名称' + '\u2022' + '姓名';
    text = $("<p></p>").html("(页眉)" + header_content+"&nbsp;").css({"font-size":header.size,"font-family":header.font,"color":"#"+header.color,"text-align":header.align,"height":margin.top,"line-height":margin.top+"px"});
    header_div.append(text);
    footer_div = $("<div></div>").attr("id","page_" + index + "_item_footer").addClass("editable").css({'margin-top':-margin.bottom,'margin-left':margin.left,'margin-right':margin.right,"height":margin.bottom}).click(edit);
    text = $("<p></p>").html("(页脚)" + footer.content.replace(/ /g,"&nbsp;")).css({"font-size":footer.size,"font-family":footer.font,"color":"#"+footer.color,"text-align":footer.align,"line-height":margin.bottom+"px"});
    footer_div.append(text);
    page.append(header_div);
    if(header.line)header_div.append("<hr style=\"margin-top:-12px;\"/>");
    $(element).each(function(i,e){
        div = $("<div></div>").attr("id","page_" + index + "_item_" + i).attr("class","editable").click(edit);
        delete_button = $("<button></button>").attr("class","btn btn-danger").html("<span class='glyphicon glyphicon-trash' aria-hidden='true'></span>").click(Delete);
        up_button = $("<button></button>").attr("class","btn btn-default").html("<span class='glyphicon glyphicon-arrow-up' aria-hidden='true'></span>").click(up);
        down_button = $("<button></button>").attr("class","btn btn-default").html("<span class='glyphicon glyphicon-arrow-down' aria-hidden='true'></span>").click(down);
        action = $("<div></div>").attr("class","action pull-right").hide();
        action.append(delete_button).append(up_button).append(down_button);
        if(e.style == 'description'){
            text = $("<p></p>").html(e.content.replace(/ /g,"&nbsp;").replace(/\n/g,"<br/>")).css({"font-size":e.size,"font-family":e.font,"color":"#"+e.color,"text-align":e.align});
            div.append(text);
        }
        else if(e.style == 'line'){
            div.append("<hr/>");
        }
        else if(e.style == 'image'){
            child = $("<div></div>").css({"text-align":e.align});
            child.append("<img width='" + e.width + "' height='" + e.height + "' src='/static/imgs/" + e.src + "'></img>");
            div.append(child);
        }
        else if(e.style == 'dimension'){
            title = e.content.replace(/ /g,"&nbsp;").replace(/\n/g,"<br/>");
            if(e.type != '0')title += "(" + select_options.type[e.type] + ")";
            text = $("<p></p>").html(title).css({"font-size":e.title_size,"font-family":e.title_font,"color":"#"+e.title_color});
            div.append(text);
            if(e.evaluation == 1){
                text = $("<p></p>").html("评价语：<br/>这里是评价语").css({"font-size":e.size,"font-family":e.font,"color":"#"+e.color});
            }
            else{
                text = $("<p></p>").html("(没有评价语)");
            }
            div.append(text);
            
        }
        else if(e.style == 'chart'){
            text = e.title;
            if(text == '')text = '(无标题)';
            text += select_options.chart_type[e.type];
            child = $("<div></div>").css({"float":e.align,"width":e.width, "height":e.height, "margin":"0 auto", "border":"solid 1px", "margin-top": "5px", "text-align":"center"});
            child.append(text);
            div.append(child).css({"height":e.height+10});
        }
        else if(e.style == 'info'){
            text = $("<p></p>").html(e.content.replace(/ /g,"&nbsp;").replace(/\n/g,"<br/>") + select_options.info[e.attr]).css({"font-size":e.size,"font-family":e.font,"color":"#"+e.color,"text-align":e.align});
            div.append(text);
        }
        else if(e.style == 'blank'){
            div.append("<br/>");
        }
        div.append(action);
        div.hover(function(){
            $(this).css({"border":"1px dashed"});
            $(this).children(".action").show();
        },function(){
            $(this).css({"border":"none"});
            $(this).children(".action").hide();
        });
        content.append(div);
    });
    page.append(content);
    pagination_div = $("<div></div>").attr("id","page_" + index + "_item_pagination").css({"margin-left":margin.left,"margin-right":margin.right,"height":margin.bottom});
    text = $("<p></p>").html("第" + (index+1) + "页/共" + template.body.length + "页").css({"font-size":template.pagination.size,"color":"#"+template.pagination.color,"text-align":template.pagination.align,"line-height":margin.bottom+"px"});
    if(index == 'cover')text.html(".").css('font-color','#FFFFFF');
    pagination_div.append(text);
    page.append(pagination_div);
    page.append(footer_div);
    $("#list").append(page);
    if(index == 'cover')$("#nav").append("<li><a href='#page_cover'>封面页</a></li>");
    else $("#nav").append("<li><a href='#page_" + index + "'>第" + (index+1) + "页</a></li>");
}

function update_chart(dimensions, norm_line){
    update_select("all_dimensions", select_options.dimensions, dimensions); 
    var leftSel = $("#all_dimensions"); 
    var rightSel = $("#chart_dimensions");   
    rightSel.html("");
    $.each(dimensions, function(i, e){
        leftSel.find("option[value=" + e + "]").remove().appendTo(rightSel);
    });
    $(".bootstrap-checkbox-list").remove();
    $('#checkboxList-normline').bootstrapCheckboxList("init");
    items = [];
    $.each(select_options.norm_line,function(k,v){
        items.push(createInfoItem(v,k,0));
    });
    res = infoItemWrapper(items);
    $('#checkboxList-normline').bootstrapCheckboxList("load",res);
    $.each(norm_line,function(i,e){
        $("#id-"+e).click();
    });
}


function get_selected_elements(name) {
    var checked = [];
    checked = checked.concat($('#checkboxList-' + name).bootstrapCheckboxList('getCheckedItems'));
    var res = []
    for (var i=0;i < checked.length;i++) {
        res.push(Number(checked[i]));
    }
    return res;
}

function get_chart_dimensions(){
    var selVal = []; 
    $("#chart_dimensions").find("option").each(function(){ 
        selVal.push(Number(this.value)); 
    }); 
    return selVal;
}

function Submit(){
    style = $(this).parents(".modal").attr("id");
    index = $("#index").val();
    order = $('#order').val();
    var element = {};
    if(order != 'header' && order != 'footer' && order != 'pagination' && order != 'margin' && order != 'background')element.style = style;
    else style = order;
    switch(style){
        case 'header':
            var $s4 = $("#description_style");
            var $s5 = $("#description_line");
            element.style = $s4[0].options[$s4[0].selectedIndex].value;
            element.line = $s5.prop("checked");
        case 'description':
        case 'footer':
            element.content = $("#description_content").val();
            element.size = Number($("#description_size").val());
            var $s1 = $("#description_font");
            var $s2 = $("#description_align");
            element.font = $s1[0].options[$s1[0].selectedIndex].value;
            element.align = $s2[0].options[$s2[0].selectedIndex].value;
            element.color = $("#description_color").val();
            break;
        case 'image':
            element.src = $("#image_src").val();
            element.width = Number($("#width").val());
            element.height = Number($("#height").val());
            var $s1 = $("#image_align");
            element.align = $s1[0].options[$s1[0].selectedIndex].value;
            break;
        case 'chart':
            var $s1 = $("#chart_type");
            var $s2 = $("#chart_way");
            var $s4 = $("#chart_score");
            var $s5 = $("#chart_align");
            element.title = $("#chart_title").val();
            element.type = $s1[0].options[$s1[0].selectedIndex].value;
            element.way = $s2[0].options[$s2[0].selectedIndex].value;
            element.norm_line = get_selected_elements('normline');
            element.score = $s4[0].options[$s4[0].selectedIndex].value;
            element.dimensions = get_chart_dimensions();
            element.width = Number($("#chart_width").val());
            element.height = Number($("#chart_height").val());
            element.color = $("#chart_color").val();
            element.align = $s5[0].options[$s5[0].selectedIndex].value;
            break;
        case 'dimension':
            var $s1=$("#Select1");
            var $s2=$("#Select2");
            var $s3=$("#Select3");
            element.id = Number($s1[0].options[$s1[0].selectedIndex].value);
            element.type = $s2[0].options[$s2[0].selectedIndex].value;
            element.evaluation = Number($s3[0].options[$s3[0].selectedIndex].value);
            element.content = $("#title_content").val();
            element.title_size = Number($("#title_size").val());
            var $s4 = $("#title_font");
            element.title_font = $s4[0].options[$s4[0].selectedIndex].value;
            element.title_color = $("#title_color").val();
            element.size = Number($("#evaluation_size").val());
            var $s5 = $("#evaluation_font");
            element.font = $s5[0].options[$s5[0].selectedIndex].value;
            element.color = $("#evaluation_color").val();
            break; 
        case 'info':
            var $s1 = $("#info_attr");
            var $s2 = $("#info_font");
            var $s3 = $("#info_align");
            element.attr = $s1[0].options[$s1[0].selectedIndex].value;
            element.font = $s2[0].options[$s2[0].selectedIndex].value;
            element.align = $s3[0].options[$s3[0].selectedIndex].value;
            element.color = $("#info_color").val();
            element.size = Number($("#info_size").val());
            element.content = $("#info_content").val();
            break;
        case 'pagination':
            element.size = Number($("#pagination_size").val());
            var $s1 = $("#pagination_align");
            element.align = $s1[0].options[$s1[0].selectedIndex].value;
            element.color = $("#pagination_color").val();
            break;
        case 'margin':
            element.left = Number($("#margin_left").val());
            element.right = Number($("#margin_right").val());
            element.top = Number($("#margin_top").val());
            element.bottom = Number($("#margin_bottom").val());
            break;
        case 'background':
            element = $("#image_src").val();
            break;
    }
    if(index == 'cover'){  
        if(order == "-1")template.cover.body.push(element);
        else if(order == 'header' || order == 'footer' || order == 'margin' || order == 'background')template.cover[order] = element;
        else template.cover.body[Number(order)] = element;
    }
    else{
        if(order == "-1")template.body[index].push(element);
        else if(order == 'header' || order == 'footer' || order == 'pagination' || order == 'margin' || order == 'background')template[order] = element;
        else template.body[Number(index)][Number(order)] = element;  
    }
    save();
    update_pages();
}
