function update_stock_chart(url, form_prefix) {
    let data;
    if(form_prefix === 'a_'){
        data = {
            "stock_time_type": $("#a_stock_time_type option:selected").val(),
            "form_start_date": $("#a_form_start_date").val(),
            "form_end_date": $("#a_form_end_date").val(),
            "interest_stock_code": $("#a_interest_stock_code option:selected").val(),
            "find_add_code": $("#a_find_add_code").val()
        }
    }else if (form_prefix === 'b_'){
        data = {
            "stock_time_type": $("#b_stock_time_type option:selected").val(),
            "form_start_date": $("#b_form_start_date").val(),
            "form_end_date": $("#b_form_end_date").val(),
            "interest_stock_code": $("#b_interest_stock_code option:selected").val(),
            "find_add_code": $("#b_find_add_code").val()
        }
    }else{
        data = {
            "stock_time_type": $("#bt_stock_time_type option:selected").val(),
            "form_start_date": $("#bt_form_start_date").val(),
            "form_end_date": $("#bt_form_end_date").val(),
            "interest_stock_code": $("#bt_interest_stock_code option:selected").val(),
            "find_add_code": $("#bt_find_add_code").val(),
            "bt_strategy": $("#bt_strategy option:selected").val(),
            "bt_data": $("#bt_data option:selected").val(),
        }
    }
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(data), // 将data转化为字符串
        contentType: 'application/json; charset=UTF-8', // 指定contentType
        dataType: "json",  // 注意：这里是指希望服务端返回的数据类型
        success: function (data) { // 返回数据根据结果进行相应的处理
            if(data['my_chart'] === 'fail'){
                alert('查找对象为空')
                return
            }
            // 替换标签的内容
            if(form_prefix === 'a_'){
                // console.log("replace area a")
                $("#a_chart_area").html(data['my_chart'])
            }else if (form_prefix === 'b_'){
                // console.log("replace area b")
                $("#b_chart_area").html(data['my_chart'])
            }else{
                // console.log("replace area bt")
                $("#bt_chart_area").html(data['my_chart'])
                $("#bt_table").html(data['bt_table'])
            }
            console.log('success')
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
}
function update_stock_form(url, form_prefix) {
    let data;
    if(form_prefix === 'a_'){
        data = {
            "stock_time_type": $("#a_stock_time_type option:selected").val(),
            "form_start_date": $("#a_form_start_date").val(),
            "form_end_date": $("#a_form_end_date").val(),
            "interest_stock_code": $("#a_interest_stock_code option:selected").val(),
            "find_add_code": $("#a_find_add_code").val()
        }
    }else if (form_prefix === 'b_'){
        data = {
            "stock_time_type": $("#b_stock_time_type option:selected").val(),
            "form_start_date": $("#b_form_start_date").val(),
            "form_end_date": $("#b_form_end_date").val(),
            "interest_stock_code": $("#b_interest_stock_code option:selected").val(),
            "find_add_code": $("#b_find_add_code").val()
        }
    }else{
        data = {
            "stock_time_type": $("#bt_stock_time_type option:selected").val(),
            "form_start_date": $("#bt_form_start_date").val(),
            "form_end_date": $("#bt_form_end_date").val(),
            "interest_stock_code": $("#bt_interest_stock_code option:selected").val(),
            "find_add_code": $("#bt_find_add_code").val()
        }
    }
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(data), // 将data转化为字符串
        contentType: 'application/json; charset=UTF-8', // 指定contentType
        dataType: "json",  // 注意：这里是指希望服务端返回的数据类型
        success: function (data) { // 返回数据根据结果进行相应的处理
            if(data['form_inline'] === 'fail'){
                return
            }
            console.log(form_prefix)
            if(form_prefix === 'a_'){
                console.log("replace form a")
                $("#a_form_inline").html(data['form_inline'])
            }else if (form_prefix === 'b_'){
                console.log("replace form b")
                $("#b_form_inline").html(data['form_inline'])
            }else{
                console.log("replace form bt")
                $("#bt_form_inline").html(data['form_inline'])
            }

            console.log('success')
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
}
function repairZero(num){
    if(num < 10){
        num = "0" + num;
    }
    return num;
}
function get_time_str(date){
    return date.getFullYear() + "-" + repairZero(date.getMonth()+1) + "-" + repairZero(date.getDate())
}
function stock_time_type_change(form_prefix) {
    let date = new Date();
    let now_date_str = get_time_str(date)
    if(form_prefix === 'b_'){
        let stock_time_type = $("#b_stock_time_type option:selected").val()
        // console.log("set end date to ", now_date_str)
        $("#b_form_end_date").val(now_date_str)
        if (stock_time_type === 'DAY'){
            $("#b_form_start_date").val(get_time_str(new Date(date.setDate(date.getDate()-400))))
        }else if(stock_time_type === '30M' || stock_time_type === '15M'){
            $("#b_form_start_date").val(get_time_str(new Date(date.setDate(date.getDate()-38))))
        }else{
            $("#b_form_start_date").val(get_time_str(new Date(date.setDate(date.getDate()-30))))
        }
    }else if (form_prefix === 'a_'){
        let stock_time_type = $("#a_stock_time_type option:selected").val()
        // console.log("set end date to ", now_date_str)
        $("#a_form_end_date").val(now_date_str)
        if (stock_time_type === 'DAY'){
            $("#a_form_start_date").val(get_time_str(new Date(date.setDate(date.getDate()-400))))
        }else if(stock_time_type === '30M' || stock_time_type === '15M'){
            $("#a_form_start_date").val(get_time_str(new Date(date.setDate(date.getDate()-38))))
        }else{
            $("#a_form_start_date").val(get_time_str(new Date(date.setDate(date.getDate()-30))))
        }
    }else{
        let stock_time_type = $("#bt_stock_time_type option:selected").val()
        // console.log("set end date to ", now_date_str)
        $("#bt_form_end_date").val(now_date_str)
        if (stock_time_type === 'DAY'){
            $("#bt_form_start_date").val(get_time_str(new Date(date.setDate(date.getDate()-400))))
        }else if(stock_time_type === '30M' || stock_time_type === '15M'){
            $("#bt_form_start_date").val(get_time_str(new Date(date.setDate(date.getDate()-38))))
        }else{
            $("#bt_form_start_date").val(get_time_str(new Date(date.setDate(date.getDate()-30))))
        }
    }
}