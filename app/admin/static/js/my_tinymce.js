$(function () {
    tinymce.init({
        selector: '.tinymce-editor',
        language: 'zh_CN',
        //skin:'oxide-dark',
        plugins: 'print preview searchreplace autolink directionality visualblocks visualchars fullscreen image link media template code codesample table charmap hr pagebreak nonbreaking anchor insertdatetime advlist lists wordcount imagetools textpattern help emoticons autosave bdmap indent2em autoresize lineheight formatpainter axupimgs',
        //toolbar: 'code undo redo | forecolor backcolor bold italic underline strikethrough link anchor | alignleft aligncenter alignright alignjustify outdent indent| bdmap |fullscreen preview',
        toolbar: 'code undo redo restoredraft | forecolor backcolor bold italic underline strikethrough link anchor | preview fullscreen | alignleft aligncenter alignright alignjustify outdent indent | \
                cut copy paste pastetext |styleselect formatselect fontselect fontsizeselect | bullist numlist | blockquote subscript superscript removeformat | \
                    table image media charmap emoticons hr pagebreak insertdatetime print | bdmap indent2em lineheight formatpainter',
        height: 650, //编辑器高度
        // height: 650, //编辑器高度
        min_height: 500,
        /*content_css: [ //可设置编辑区内容展示的css，谨慎使用
            '/static/reset.css',
            '/static/ax.css',
            '/static/css.css',
        ],*/
        fontsize_formats: '12px 14px 16px 18px 24px 36px 48px 56px 72px',
        font_formats: '微软雅黑=Microsoft YaHei,Helvetica Neue,PingFang SC,sans-serif;苹果苹方=PingFang SC,Microsoft YaHei,sans-serif;宋体=simsun,serif;仿宋体=FangSong,serif;黑体=SimHei,sans-serif;Arial=arial,helvetica,sans-serif;Arial Black=arial black,avant garde;Book Antiqua=book antiqua,palatino;',
        /*link_list: [
            { title: '预置链接1', value: 'http://www.tinymce.com' },
            { title: '预置链接2', value: 'http://tinymce.ax-z.cn' }
        ], */
        /*image_list: [
            { title: '预置图片1', value: 'https://www.tiny.cloud/images/glyph-tinymce@2x.png' },
            { title: '预置图片2', value: 'https://www.baidu.com/img/bd_logo1.png' }
        ],*/
        convert_urls: false,
        image_class_list: [
            { title: 'None', value: '' },
            { title: 'Some class', value: 'class-name' }
        ],
        importcss_append: true,
        file_picker_types: 'file image media',
        //自定义文件选择器的回调内容
        file_picker_callback: function (callback, value, meta) {
            //文件分类
            var filetype = '.pdf, .txt, .zip, .rar, .7z, .doc, .docx, .xls, .xlsx, .ppt, .pptx, .mp3, .mp4';
            //后端接收上传文件的地址
            var upurl = '/admin/upload';
            //为不同插件指定文件类型及后端地址
            switch (meta.filetype) {
                case 'image':
                    filetype = '.jpg, .jpeg, .png, .gif, .webp';
                    upurl = upurl;
                    break;
                case 'media':
                    filetype = '.mp3, .mp4';
                    upurl = upurl;
                    break;
                case 'file':
                default:
            }

            //模拟出一个input用于添加本地文件
            var input = document.createElement('input');
            input.setAttribute('type', 'file');
            input.setAttribute('accept', filetype);
            input.click();
            input.onchange = function () {
                var file = this.files[0];
                var formData = new FormData();
                formData.append('file', file, file.name);
                formData.append('folder', 'material')
                $.ajax({
                    url: upurl,
                    type: "post",
                    data: formData,
                    processData: false, // 告诉jQuery不要去处理发送的数据
                    contentType: false, // 告诉jQuery不要去设置Content-Type请求头
                    dataType: 'json',
                    success: function (resp) {
                        console.log(resp)
                        callback(resp.data)
                    },
                    error: function (err) {
                        console.error(err)

                    }
                });

            };
        },
        toolbar_sticky: true,
        autosave_ask_before_unload: false,
        fullscreen_native: true,
    });
});