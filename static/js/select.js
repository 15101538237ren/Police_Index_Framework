/**
 * Created by ren on 15/8/3.
 */
  /**
   * 全选
   *
   * items 复选框的name
   */
  function allCkb(items){
     $('[name='+items+']:checkbox').each( function() {
         $(this).attr('checked', true);
         $(this).parents('.checkbox').find('span').addClass('checked');
     });
  }

  /**
   * 全不选
   *
   */
  function unAllCkb(items){
     $('[name='+items+']:checkbox').each( function() {
         $(this).attr('checked', false);
         $(this).parents('.checkbox').find('span').removeClass('checked');
     });
  }

  /**
   * 反选
   *
   * items 复选框的name
   */
  function inverseCkb(items){
     $('[name='+items+']:checkbox').each(function(){
        //此处用jq写法颇显啰嗦。体现不出JQ飘逸的感觉。
     //$(this).attr("checked", !$(this).attr("checked"));

     //直接使用js原生代码，简单实用
     this.checked=!this.checked;
     });
  }