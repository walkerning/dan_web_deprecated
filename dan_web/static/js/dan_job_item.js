!function ($) {

  $(document).ready(function () {
    var $delete_job_btn = $('button#delete_job_btn');
    var $run_job_btn = $('button#run_job_btn');
    var $stop_job_btn = $('button#stop_job_btn');
    var $log_job_btn = $('button#log_job_btn');
    var $log_terminal = $('div.log_terminal');

    function _post(url, method, data) {
      var form = $("<form>").attr({
        method: method,
        action: url
      }).css({
        display: 'none'
      });

      // add all data
      for (var name in data) {
        form.append($("<input>").attr({
          type: 'hidden',
          name: name,
          value: data[name]
        }));
      }

      // submit the form
      form.appendTo('body').submit();

    }

    function p_generate(log) {
      return '<p class="log_text">' + log + '</p>';
    }

    function scroll_terminal() {
      // auto scroll to the bottom when new log is appended
      $log_terminal.scrollTop($log_terminal[0].scrollHeight);
    }

    function get_realtime_log() {
      // 浏览器直接用websocket连接
      var ws = new WebSocket("ws://" + location.host + REALTIME_LOG_URL);
      $log_job_btn.addClass("disabled");
      $log_terminal.children().remove();
      ws.onmessage = function(res) {
        $log_terminal.append(p_generate(res.data));
        scroll_terminal();
      };
      ws.onerror = function(res) {
        $log_terminal.append(p_generate("连接中断"));
        $log_job_btn.removeClass("disabled");
        scroll_terminal();
      };
      ws.onclose = function(res) {
        $log_terminal.append(p_generate("------ END LOG ------"));
        $log_job_btn.removeClass("disabled");
        scroll_terminal();
      };
      ws.onopen = function () {
        $log_terminal.css('height', '300px');
        $log_terminal.append(p_generate("----- BEGIN LOG -----"));
        ws.send(current_job_id);
      };

    }

    function ajax_post_job_operation (post_url, success_info, callback) {
      return function () {
	$(this).addClass('disabled');
        $.ajax({
          url: post_url,
          method: 'POST',
          data: {
            job: current_job_id
          },
          success: function (res) {
	    $(this).removeClass("disabled");
            if (res.status == "success") {
              if (success_info) {
                displayString(success_info);
              }
              if (callback) {
                callback();
              }
            }
            else {
              displayError(res.error_string);
            }
          }
        });
      };
    }

    function displayError (error_string) {
      $("#status_string").css('color', '#690F0D').text(error_string);
    }
    function displayString (string) {
      $("#status_string").css('color', 'green').text(string);
    }

    // fixme: maybe all use non-ajax post here!
    $log_job_btn.click(get_realtime_log);
    $run_job_btn.click(ajax_post_job_operation(RUN_JOB_URL, "运行Job成功, 请刷新页面"));
    $delete_job_btn.click(function () {
      _post(DELETE_JOB_URL, 'POST', {'job': current_job_id});
    });
    $stop_job_btn.click(ajax_post_job_operation(STOP_JOB_URL, "中止Job成功, 请刷新页面"));
  });
}(jQuery);
