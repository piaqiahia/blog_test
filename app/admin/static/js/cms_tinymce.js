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
        max_height: 650,
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
			if (meta.filetype === 'file') {
				callback('https://www.baidu.com/img/bd_logo1.png', { text: 'My text' });
			}
			if (meta.filetype === 'image') {
				imagehosting('editor-img')
				tinymce_select_img_callback = callback;
				// callback('https://www.baidu.com/img/bd_logo1.png', { alt: 'My alt text' });
			}
			if (meta.filetype === 'media') {
				callback('movie.mp4', { source2: 'alt.ogg', poster: 'https://www.baidu.com/img/bd_logo1.png' });
			}
		},
        toolbar_sticky: true,
        autosave_ask_before_unload: false,
        fullscreen_native: true,
    });
});