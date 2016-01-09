!function($) {
  function ajax_upload(evt) {
    // Create a new FormData object.
    evt.preventDefault();
    var formData = new FormData();
    var to_upload_file = $("#file_select")[0].files[0];
    var to_upload_file_type = $("#upload_file_type")[0].value;
    formData.append('file', to_upload_file, to_upload_file.name);
    formData.append('filetype', to_upload_file_type);

    // Set up the request.
    var xhr = new XMLHttpRequest();
    // 展示uploading的进度条
    xhr.upload.addEventListener("progress", uploadProgress, false);
    xhr.onreadystatechange =  function () {
      if (xhr.readyState==4) {
        if (xhr.status==200){
          var data = $.parseJSON(xhr.responseText);
          var upload_status = data['status'];

          if (upload_status == 'success'){
            console.log('successfully uploaded file');
            displayString('成功上传');
            refresh_file_list('upload_' + to_upload_file_type);
          }
          else if (upload_status == 'fail'){
            console.log('failed to upload file');
            displayError(data['error_string']);
          }
        }
        else {
          displayError('Encounter error: ' + xhr.status);
        }

      }
    };
    // Open the connection.
    xhr.open('POST', UPLOAD_URL, true);

    // reset the upload file progress bar
    clearUploadStatus();

    // Send the Data.
    xhr.send(formData);
  }

  function clearUploadStatus () {
    $('#upload_file_bar').removeClass('progress-bar-danger').addClass('progress-bar-succes').css('width', '0%');
    $('#status_string').text('');
  }

  function uploadProgress (evt) {
    if (evt.lengthComputable) {
      var percentComplete = evt.loaded / evt.total * 100;
      //Do something with download progress
      $('#upload_file_bar').css('width', percentComplete + '%');
    }

  }

  function displayError (error_string) {
    $("#status_string").css('color', '#690F0D').text(error_string);
    $("#upload_file_bar").removeClass('progress-bar-success').addClass('progress-bar-danger');
  }

  function displayString (string) {
    $("#status_string").css('color', 'green').text(string);
  }

  /* delete file */
  function delete_file (dir_name, filename) {
    $.ajax({
      url: DELETE_FILE_URL,
      type: 'POST',
      data: {
        'dir_name': dir_name,
        'file_name': filename
      },
      success: function (response) {
        if (response.status == 'success') {
          $("table#" + dir_name + " tr[name='" + filename + "']").remove();
          // file number - 1
          var file_num_ele = $(".file_num[name='" + dir_name + "']");
          file_num_ele.html(file_num_ele.html() - 1);
        }
        else
          swal("删除文件出错", response.error_string);
      }
    });
  }

  /* download file */
  function download_file (dir_name, filename) {
    /*$('<form action="/download_file/"' + filename + ' method="POST">' +
     '<input type="hidden" name="dir_name" value="' + dir_name + '">' +
     '<input type="hidden" name="file_name" value="' + filename +'">' +
     '</form>').submit();*/
    // get seems more appropriate, browser downloader could recognized the
    // base filename instead of "download_file"
    window.open('/download_file/' + filename + '?dir_name=' + dir_name);
  }

  function refresh_file_list (dir_name) {
    $.ajax({
      url: REFRESH_FILE_LIST_URL,
      type: 'POST',
      data: {
        'dir_name': dir_name
      },
      success: function(response){
        // get the table to update
        if (response.status != 'success') {
          swal("更新文件列表出错", response.error_string);
          return;
        }
        var this_table = $("table#" + dir_name);
        this_table.empty();
        var this_tbody = $("<tbody>");
        this_table.append(this_tbody);

        // push into the file name list
        for (var index in response.file_list) {
	  var fileinfo = response.file_list[index];
          var filename = fileinfo['name'];
	  var filesize = fileinfo['size'];
          var new_tr = $("<tr>", {name: filename});

          // filename td
          var filename_td = $("<td>");
          filename_td.addClass('filename_td')
            .css('white-space', 'nowrap')
            .css('overflow', 'hidden')
            .css('width', '110px')
            .attr('data-toggle', 'tooltip')
            .attr('title', filename + ' 大小: ' + filesize)
            .attr('data-original-title', filename)
            .attr('data-placement', 'bottom');
          filename_td.append('<p class="file_name_item">' + filename + '</p>' );

          // delete td
          var delete_td = $("<td>",  {style: 'width: 40px'});
          var delete_btn = $("<a>", {
            name: filename,
            dir_name: dir_name,
            class: "btn mini delete_file btn-danger"
          });
          delete_btn.html('删除');
          delete_td.append(delete_btn);

          // download td
          var download_btn = $("<a>", {
            name: filename,
            dir_name: dir_name,
            class: "btn mini download_file btn-info"});
          download_btn.html('下载');
          var download_td = $("<td>", {style: 'width: 40px'});
          download_td.append(download_btn);
          new_tr.append(filename_td);
          new_tr.append(delete_td);
          new_tr.append(download_td);
          this_tbody.append(new_tr);
        }
        // show file number
        $(".file_num[name='" + dir_name +"']").html(response.file_list.length);

        // register event handler for these buttons
        $("a.download_file[dir_name='" + dir_name + "']").click(function () {
          var filename = $(this).attr('name');
          var dir_name = $(this).attr('dir_name');
          download_file(dir_name, filename);
        });
        $("a.delete_file[dir_name='" + dir_name + "']").click(function () {
          var filename = $(this).attr('name');
          var dir_name = $(this).attr('dir_name');
          // confirm delete
          var confirm_res = confirm("你确定要删除吗?");
          if (confirm_res)
            delete_file(dir_name, filename);
        });
      }
    }); // end $.ajax
  } // end function refresh_file_list

  $("document").ready(function(){
    $("#file_upload_btn").click(ajax_upload);
    $(".refresh_file_list").click(function () {
      var this_id = $(this).attr('id');
      refresh_file_list(this_id);
    });
    $(".refresh_file_list").trigger('click');

  });

}(jQuery);
