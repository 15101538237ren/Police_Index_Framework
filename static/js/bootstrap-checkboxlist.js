/**
 * Created by talus on 15/9/4.
 */
(function ($) {

    var formatData = function(data, $bootstrap_checkbox_list) {
        if (data === null || data === undefined) {
            return data;
        }

        if (!data.hasOwnProperty('head')) {
            data['head'] = [$bootstrap_checkbox_list.options.default_head];
        }
        //console.log("data after formated:");
        //console.log(data);

        //console.log(data.head);
        var head = data.head[0];
        if (head.status == 1) {
            $.each(data.body, function(){
                this.status = 1;
            });
            return data;
        }

        //console.log(data.body);
        var selected = 0;
        $.each(data.body, function(){
            if (this.status == 1){
                selected += 1;
            }
        });
        if(selected == data.body.length) {
            head.status = 1;
        }
        return data;
    };

    var BootstrapCheckBoxList = function (el, options) {
        this.options = options;
        this.$el = $(el);
        this.$el_ = this.$el.clone();
        this.timeoutId_ = 0;
        this.timeoutFooter_ = 0;

        this.init();
    };

    BootstrapCheckBoxList.DEFAULTS = {
        'data': [],
        'settings': {
            on: {
                icon: 'glyphicon glyphicon-check'
            },
            off: {
               icon: 'glyphicon glyphicon-unchecked'
            }
        },
        'color': "primary",
        'style': "list-group-item-",
        'total': undefined,
        'default_head': {
            "value":"checkAll",
            "label": "全选",
            "status":"0"
        },
        onCheckAll: function () {
            return false;
        },
        onCheck: function(index, value, $element) {
            return false;
        },
        onUnCheckAll: function() {
            return false;
        },
        onUnCheck: function(index, value, $element) {
            return false;
        },
        onChange: function(index, value, $element) {
            return false;
        }
    };

    BootstrapCheckBoxList.EVENTS = {
        'checkall.bs.checkbox-list': 'onCheckAll',
        'check.bs.checkbox-list': 'onCheck',
        'uncheck.bs.checkbox-list': 'onUnCheck',
        'uncheckall.bs.checkbox-list': 'onUnCheckAll'
    };

    BootstrapCheckBoxList.prototype.init = function () {
        //console.log('init');
        this.initContainer();
        this.initData();
    };

    BootstrapCheckBoxList.prototype.initContainer = function() {
        //console.log('initContainer');
        this.$container = $([
            '<div class="bootstrap-checkbox-list">',
                '<div class="check-list-container well" style="max-height: 300px;overflow: auto;">',
                    '<ul id="check-list-header" class="list-group checked-list-box">',
                    '</ul>',
                    '<br>',
                    '<ul id="check-list-body" class="list-group checked-list-box">',
                    '</ul>',
                    '<br />',
                '</div>',
            '</div>'
        ].join(''));

        this.$container.insertAfter(this.$el);
        this.$checkListHead = this.$container.find('#check-list-header');
        this.$checkListBody = this.$container.find('#check-list-body');
        this.$checkListContainer = this.$container.find('.check-list-container');
    };

    BootstrapCheckBoxList.prototype.initData = function(data) {
        //console.log('initData');
        if (data === null || (data === undefined)) {
            return false;
        }

        var bootstrap_checkbox_list = this;
        var headItem = this.options.default_head;
        if (data.hasOwnProperty('head')) {
            headItem = data.head[0];
        }
        this.addHeader(headItem);

        this.options.total = data.body.length;
        $.each(data.body, function(idx, obj){
            bootstrap_checkbox_list.appendItem(obj);
        });
        this.initEventListener();
    };

    BootstrapCheckBoxList.prototype.initEventListener = function() {
        var $bootstrap_checkbox_list = this;

        //body listener
        this.$checkListBody.find('.list-group-item').each(function() {
            $(this).click(function() {
                $bootstrap_checkbox_list.changeStatus($(this));

                var selected = $bootstrap_checkbox_list.getCheckedNumber();
                var total = $bootstrap_checkbox_list.options.total;
                $bootstrap_checkbox_list.$checkListHead.find('.list-group-item').each(function() {
                    var headChecked = $(this).find('input').is(":checked");
                    if ((total > selected && headChecked) || (total == selected && !headChecked)) {
                        $bootstrap_checkbox_list.changeStatus($(this));
                    }
                    //console.log("headChecked=" + headChecked);
                });
            });
        });

        //head listener
        this.$checkListHead.find('.list-group-item').each(function() {
            $(this).click(function() {
                $bootstrap_checkbox_list.changeStatus($(this));
                $bootstrap_checkbox_list.$checkListBody.find('.list-group-item').each(function() {
                    $bootstrap_checkbox_list.changeStatus($(this));
                });
            });
        });
    };

    BootstrapCheckBoxList.prototype.createItem = function(item) {
        var inner = [
            '<li id="name" class="list-group-item">131</li>',
        ].join('');

        var $widget = $(inner),
            $checkbox = $('<input type="checkbox" class="hidden" />');

        $widget.attr("id","id-"+item.value);
        $widget.attr("value",item.value);
        $widget.text(item.label);

        $widget.css('cursor', 'pointer');
        $widget.append($checkbox);
        if (item.status == 1) {
            $checkbox.prop('checked', true);
        }

        $widget = this.updateDisplay($widget);
        if ($widget.find('.state-icon').length == 0) {
            $widget.prepend('<span class="state-icon ' + this.options.settings[$widget.data('state')].icon + '"></span>');
        }
        return $widget;
    };

    BootstrapCheckBoxList.prototype.changeStatus = function($widget) {
        var $checkbox = $widget.find('input');
        $checkbox.prop('checked', !$checkbox.is(':checked'));
        this.updateDisplay($widget);
    };

    BootstrapCheckBoxList.prototype.updateDisplay = function($widget) {
        var $checkbox = $widget.find('input');
        var isChecked = $checkbox.is(':checked');

        // Set the button's state
        $widget.data('state', (isChecked) ? "on" : "off");
        // Set the button's icon
        $widget.find('.state-icon')
            .removeClass()
            .addClass('state-icon ' + this.options.settings[$widget.data('state')].icon);

        // Update the button's color
        if (isChecked) {
            $widget.addClass(this.options.style + this.options.color + ' active');
        } else {
            $widget.removeClass(this.options.style + this.options.color + ' active');
        }
        return $widget;
    };

    BootstrapCheckBoxList.prototype.checkAll = function() {
        //console.log("function");
    };

    BootstrapCheckBoxList.prototype.load = function(data) {
        //console.log("load");
        var data = formatData(data, this);
        this.initData(data);
    };

    BootstrapCheckBoxList.prototype.addHeader = function(headItem) {
        var $widget = this.createItem(headItem);
        this.$checkListHead.append($widget);
    };

    BootstrapCheckBoxList.prototype.appendItem = function(obj) {
        var $widget = this.createItem(obj);
        this.$checkListBody.append($widget);
    };

    BootstrapCheckBoxList.prototype.getCheckedItems = function() {
        var checked = [];
        this.$checkListBody.find('.list-group-item.active').each(function(){
            checked.push($(this).attr('value'));
        });
        return checked;
    };

    BootstrapCheckBoxList.prototype.getCheckedHeads = function() {
        var checked = [];
        this.$checkListHead.find('.list-group-item.active').each(function(){
            checked.push($(this).attr('value'));
        });
        return checked;
    };

    BootstrapCheckBoxList.prototype.getCheckedNumber = function() {
        //console.log("getCheckedNumber");
        return this.$checkListBody.find('.list-group-item.active').length;
    };

    var allowedMethods = [
        'init',
        'load',
        'getCheckedItems',
        'getCheckedNumber',
        'getCheckedHeads'
    ];

    $.fn.bootstrapCheckboxList = function(option) {
        var value,
            args = Array.prototype.slice.call(arguments, 1);

        this.each(function () {
            var $this = $(this),
                data = $this.data('bootstrap.checkboxlist'),
                options = $.extend({}, BootstrapCheckBoxList.DEFAULTS, $this.data(),
                    typeof option === 'object' && option);

            if (typeof option === 'string') {
                if ($.inArray(option, allowedMethods) < 0) {
                    throw new Error("Unknown method: " + option);
                }

                if (!data) {
                    return;
                }

                value = data[option].apply(data, args);

                if (option === 'destroy') {
                    $this.removeData('bootstrap.checkboxlist');
                }
            }

            if (!data) {
                $this.data('bootstrap.checkboxlist', (data = new BootstrapCheckBoxList(this, options)));
            }
        });
        return typeof value === 'undefined' ? this : value;
    };
    $.fn.bootstrapCheckboxList.Constructor = BootstrapCheckBoxList;
    $.fn.bootstrapCheckboxList.defaults = BootstrapCheckBoxList.DEFAULTS;
    $.fn.bootstrapCheckboxList.methods = allowedMethods;

    // BOOTSTRAP CheckBoxList INIT
    // =======================

    $(function () {
        $('[data-toggle="checkboxList"]').bootstrapCheckboxList();
    });

})(jQuery);