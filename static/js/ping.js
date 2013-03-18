/**
 * Created with PyCharm.
 * User: alex
 * Date: 13-3-15
 * Time: 下午3:27
 * To change this template use File | Settings | File Templates.
 */

function post_ip_form_data(){
    var url = $("#ip_add_form").attr("action");
    var data = {
        addr:$("#ip_addr").val(),
        comment:$("#comment").val()
    };
    $.post(url,data,function(rt){
        if (rt.rs){
            $("#add_ip").modal('hide');
            location.reload();
        }else{
            $("#add_alert_holder").html(ip_alert_tmp({info:rt.info}));
            $(".alert").alert();
        }
    },'json');
}