!function($) {
  function ajax_upload(form_obj) {
    form_obj.submit(function (event) {
      event.preventDefault();

      // Create a new FormData object.
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
      xhr.open('POST', '/upload/', true);

      // reset the upload file progress bar
      clearUploadStatus();

      // Send the Data.
      xhr.send(formData);
    });
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
    $("#status_string").css('color', 'red').text(error_string);
    $("#upload_file_bar").removeClass('progress-bar-success').addClass('progress-bar-danger');
  }

  function displayString (string) {
    $("#status_string").css('color', 'green').text(string);
  }

  $("document").ready(function(){
    ajax_upload($("#upload_form"));
  });

}(jQuery);
