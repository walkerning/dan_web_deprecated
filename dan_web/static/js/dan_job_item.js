!function ($) {

  $(document).ready(function () {
    var $delete_job_btn = $('button#delete_job');
    var $stop_job_btn = $('button#stop_job');
    var $log_job_btn = $('button#log_job');
    var $log_terminal = $('div.log_terminal');

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

    $log_job_btn.click(get_realtime_log);
  });
}(jQuery);
