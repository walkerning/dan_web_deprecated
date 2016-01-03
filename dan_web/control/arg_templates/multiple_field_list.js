{% set col_size = 8 / FIELD_LIST|length %}
$("button[name={{ ARG_NAME }}]").click(function (evt) {
    evt.preventDefault();
    var new_field_row = $("<row>").attr({
	'class': 'multi'
    });
    new_field_row.append($("<div>").attr({
	'class': 'col-lg-4'
    }));
    {% for field in FIELD_LIST %}
    var new_col_field = $("<div>").attr({
	'class': 'col-lg-{{ col_size|int }}'
    });
    new_col_field.append($("<input>").attr({
	type: "{{ field['type'] }}",
	name: "{{ field['name'] }}",
	style: "width: 65%"
    }));
    new_field_row.append(new_col_field);
    {% endfor %}

    $(this).closest("div.form-group").find('div.multi').append(new_field_row);
});

