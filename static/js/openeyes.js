/**
 * Created by Administrator on 2019/7/30.
 */
//字符串格式化
String.prototype.format = function () {
    var values = arguments;
    return this.replace(/\{(\d+)\}/g, function (match, index) {
        if (values.length > index) {
            return values[index];
        } else {
            return "";
        }
    });
};
//弹窗
function yuAlert(state, head, body, timeout, show) {
    var timeout = arguments[3] ? arguments[3] : 5000;
    var show = arguments[4] ? arguments[4] : 'slideDown';
    setTimeout(function () {
        toastr.options = {
            closeButton: true,
            progressBar: true,
            showMethod: show,
            timeOut: timeout
        };
        if (state == 'success') toastr.success(body, head);
        else if (state == 'warning') toastr.warning(body, head);
        else if (state == 'info') toastr.info(body, head);
        else toastr.error(body, head);
        //{#        }, 1300);#}
    }, 500);
}
//主题
function theme(defaultTheme) {
    $("body").removeClass("skin-1");
    $("body").removeClass("skin-3");
    $("body").addClass(defaultTheme);
    // Default skin
    $('.s-skin-0').click(function () {
        $("body").removeClass("skin-1");
        $("body").removeClass("skin-3");
        setTheme('theme', 'skin-0')
    });
    // Blue skin
    $('.s-skin-1').click(function () {
        $("body").removeClass("skin-3");
        $("body").addClass("skin-1");
        setTheme('theme', 'skin-1')
    });
    // Yellow skin
    $('.s-skin-3').click(function () {
        $("body").removeClass("skin-1");
        $("body").addClass("skin-3");
        setTheme('theme', 'skin-3')
    });
    function setTheme(action, theme) {
        console.log(1);
        $.ajax({
            url: '/system/systemconfig/',
            type: 'POST',
            data: {'action': action, 'theme': theme},
            dataType: 'JSON',
            traditionail: true,
            headers: {'X-CSRFtoken': $.cookie('csrftoken')},
            success: function (obj) {}
        })
    }
}
function simpleLoad(btn, state) {
    if (state) {
        btn.children().addClass('fa-spin');
        btn.contents().last().replaceWith(" Loading");
    } else {
        setTimeout(function () {
            btn.children().removeClass('fa-spin');
            btn.contents().last().replaceWith(" 刷新");
        }, 2000);
    }
}
function checkRadio() {
    $('.i-checks').iCheck({
        checkboxClass: 'icheckbox_square-green',
        radioClass: 'iradio_square-green'
    });

    var checkAll = $('.checkall');
    var checkboxes = $("input[name='input[]']");
        // 全部选中或者不选.
    checkAll.on('ifChecked ifUnchecked', function(event) {
        if (event.type == 'ifChecked') {
            checkboxes.iCheck('check');
        } else {
            checkboxes.iCheck('uncheck');
        }
    });
}
function timeOut(time) {
    setTimeout(function(){ location.href = "/authen/logout/" },1000*60*time)
}