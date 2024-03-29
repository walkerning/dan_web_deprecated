!function($) {
  function option_generate(name) {
    return '<option value="' + name + '">' + name + '</option>';
  }

  function bind_remove_listeners (creator) {
    var creator_name = creator.attr("name");
    creator.on("remove", function() {
      $(".form-group[create_by='" + creator_name + "']").remove();
    });
  }

  function is_required (obj) {
    return obj.closest('div').hasClass('required');
  }

  function get_value (obj) {
    if ($(obj).attr('type') == 'checkbox') {
      return obj.checked;
    } // 还有radio button
    else {
      return $(obj).val();
    }
  }

  function post_create_job (event) {
    event.preventDefault();
    // create a hidden form
    var form = $("<form>").attr({
      method: 'POST',
      action: CREATE_JOB_URL
    }).css({
      display: 'none'
    });

    // add all non-empty configs
    $(".form-control, .form-control1").each(function (index) {
      var name = $(this).attr('name');
      var value = $(this).val();
      if (value) {
        form.append($("<input>").attr({
          type: 'hidden',
          name: name,
          value: value
        }));
      }
    });
      
    // add multiple fields configs
    $("div.multi").each(function (index) {
      var name = $(this).attr('name');
      var multi_list = [];
      $(this).find('row.multi').each(function (index) {
        var subform = {};
        $(this).find('input').each(function (ind) {
       	    subform[$(this).attr('name')] = get_value(this);
        });
	multi_list.push(subform);
      });

      form.append($("<input>").attr({
	type: 'hidden',
        name: name,
	value: JSON.stringify(multi_list)
      }));
    });

    // submit the form
    form.appendTo('body').submit();
  }

  function bind_event_listeners (prepend_selector, append_selector) {
    var selector_pre_ajax = "button.pre_ajax";
    var selector_post_ajax = "select.post_ajax";

    if (prepend_selector) {
      selector_pre_ajax = prepend_selector + selector_pre_ajax;
      selector_post_ajax = prepend_selector + selector_post_ajax;
    }
    if (append_selector) {
      selector_pre_ajax += append_selector;
      selector_post_ajax += append_selector;
    }

    // bind listeners
    $(selector_pre_ajax).click(function (evt) {
      evt.preventDefault();
      var this_name = $(this).attr('name');
      var $this_select = $("select[" + "name='" + this_name +"']");
      $.ajax({
        url: FORM_PRE_AJAX_URL,
        method: "POST",
        data: {
          name: this_name
        },
        success: function (response) {
          if (response.status == 'success') {
            // remove old options
            $this_select.children().remove();

            // insert new options
            for (var index in response.data) {
              $this_select.append(option_generate(response.data[index]));
            }
          }
          else {
            swal("Fail retrieving new option lists, please refresh again.");
          }
        }
      });
    });

    $(selector_post_ajax).change(function () {
      /* post ajax 应该都是用来create form的吧, 现在想不出其他的, 以后有的话再加*/
      var $this = $(this);
      var this_name = $(this).attr("name");
      var this_value = $(this).val();
      var this_create_by_list = [];
      var loop_item = $this;

      if (!this_value) {
        // 如果为空, 直接删掉这个选项创建的其他表单
        $("div.form-group[create_by='" + this_name + "']").remove();
        return;
      }

      while (1) {
        var this_create_by_name = loop_item.closest('div.form-group').attr("create_by");
        if (!this_create_by_name) {
          break;
        }
        var this_create_by_ele = $("div.form-group[name='" + this_create_by_name + "']");
        if (this_create_by_ele) {
          var child_value_ele = this_create_by_ele.find('.form-control, .form-control1');
          var this_create_by_value = child_value_ele.val();

          this_create_by_list.push({name: this_create_by_name,
                                    value: this_create_by_value});
          loop_item = this_create_by_ele;
        }
        else {
          break;
        }
      }

      $.ajax({
        url: FORM_POST_AJAX_URL,
        method: "POST",
        dataType: "json",
        data: {data: JSON.stringify({
          name: this_name,
          value: this_value,
          create_by_list: this_create_by_list
        })},
        success: function (response) {
          if (response.status == 'success') {
            // 把原有的那些删掉[create_by=]
            $("div.form-group[create_by='" + this_name + "']").remove();

            // 加入表单
            $this.closest("div.form-group").after(response.data);

            // 执行js
	    eval(response.js);

            // bind event listeners for these new elements
            bind_event_listeners("div.form-group[create_by='" + this_name + "'] ");
            // bind remove listener
            bind_remove_listeners($this);
            // set required property
            $("div.required > .form-control, .form-control1").prop('required', true);
          }
          else {
            swal("获取新表单失败, 请重新刷新", response.error_string);
          }
        }
      });

    });

    // trigger the first update for pre ajax selectors
    $(selector_pre_ajax).trigger('click');

  }

  $(document).ready(function(){
    bind_event_listeners();
    $("div.required > .form-control, .form-control1").prop('required', true);
    $("#upload_form").submit(post_create_job);
  });
}(jQuery);
