var qrcode = new QRCode('qrcode', {
    text: '数据加载失败',
    width: 256,
    height: 256,
    colorDark: '#000000',
    colorLight: '#ffffff',
    correctLevel: QRCode.CorrectLevel.H
});

var countdownInterval = null;
var order_no = null;

$(function () {

    $(".pay_article").click(function () {
        let articleid = $(this).data("articleid");
        let price = $(this).data("price");
        let data = {
            'article_id': articleid,
            'price': price,
        }
        $.ajax({
            url: '/article/pay/',
            type: "post",
            data: data,
            dataType: 'json',
            success: function (res) {
                console.log(res)
                if (res.code == 0) {
                    // toastr.success(res.msg);
                    order_no = res.data.out_trade_no
                    qrcode.clear()
                    qrcode.makeCode(res.data.qrcode_url)
                    clearInterval(countdownInterval)
                    countdown(60 * 5); // 60秒倒计时
                } else {
                    toastr.error(res.msg);
                }
            },
            error: function(xhr) {
                window.location.href = '/login?next=' + window.location.pathname
            },
            fail: function (res) {
                toastr.error('网络错误');
            }
        })

        $('#modal-pay').modal({
            keyboard: false,
            show: true,
        })
        return false;
    });

    $('#modal-pay').on('hidden.bs.modal', function (event) {
        clearInterval(countdownInterval); // 清除计时器
    })
});

function countdown(seconds) {
    var remainingSeconds = seconds;
    countdownInterval = setInterval(function () {
        if (remainingSeconds <= 0) {
            clearInterval(countdownInterval); // 清除计时器
            // $('#send-yzm-btn').prop('disabled', false)
            // $('#countdown-container').text('发送邮件验证码')
            // TODO: 倒计时结束之后的逻辑
        } else {
            // 更新剩余时间并显示出来
            remainingSeconds--;
            var countdownContainer = document.getElementById("countdown-container");
            countdownContainer.textContent = remainingSeconds + "秒后过期";
            is_pay()
        }
    }, 1000);

}

//是否支付
function is_pay() {
    var formData = new FormData()
    formData.append('order_no', order_no)
    $.ajax({
        url: '/is_pay/',
        type: "post",
        data: { 'order_no': order_no },
        dataType: 'json',
        success: function (res) {
            // console.log(res)
            if (res.code == 0) {
                toastr.success(res.msg);
                clearInterval(countdownInterval)
                toastr.success('支付成功')
                //刷新当前界面
                window.location.href = window.location.href
            } else {

            }
        },
        fail: function (res) {
            toastr.error('网络错误');
        }
    });
}