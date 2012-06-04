$(function(){
    
    var filter = "";

    function refresh_details(section, name) {
        var template = $.ajax({url:"/static/templates/" + section + "_details.html", async: false}).responseText;
        var details = $.parseJSON($.ajax({url: "/project/" + name, dataType: "json", async: false}).responseText);
        var builds = $.parseJSON($.ajax({url: "/build/" + name, dataType: "json", async: false}).responseText);
        $("#" + section + "-" + name + "-details").html($.mustache(template, { builds: builds, details: details }));
        $("#" + section + "-overview-" + name).find("#testing").html(details['last_tag_testing']);
        $("#" + section + "-overview-" + name).find("#unstable").html(details['last_tag_unstable']);
        $("#" + section + "-overview-" + name).find("#stable").html(details['last_tag_stable']);
        $("table[class*=tablesorter]").tablesorter();

        $("a[id='build-log-show']").click(function () {
                var build_id = $(this).attr("build_id");
                show_log(name, build_id);
                $.doTimeout('refresh-log', 2000, function () {

                    if ($("#auto-refresh:checked").length > 0) {
                        show_log(name, build_id);
                    }
                    return true;
                });
        });

        $("#action-clear-" + name).click(function(e) {
            $.post("/clear/" + name, '', function(data) {
                    $("#alert-area-" + name).html('<div class="alert alert-success"><a class="close" data-dismiss="alert">x</a><b>Clear status</b> : ' + data + '</div>');
                    $("#alert-area-" + name).alert();
                }
            );
        });

        $("#action-delete-" + name).click(function(e) {
            show_confirm_delete(name);
        });

        $("#action-enable-experimental-" + name).click(function(e) {
            $.ajax({type: "PUT", url: "/project/" + name, dataType: 'json', data: '{"experimental":1}', success: function(data) {
                    $("#alert-area-global").html('<div class="alert alert-success fade in"><a class="close" data-dismiss="alert">x</a><b>Experimental enabled</b> : ' + name + '</div>');
                    $("#alert-area-global").alert();
                    refresh_details(section, name);
                }
            });
        });

        $("#action-disable-experimental-" + name).click(function(e) {
            $.ajax({type: "PUT", url: "/project/" + name, dataType: 'json', data: '{"experimental": 0}', success: function(data) {
                    $("#alert-area-global").html('<div class="alert alert-success fade in"><a class="close" data-dismiss="alert">x</a><b>Experimental disabled</b> : ' + name + '</div>');
                    $("#alert-area-global").alert();
                    refresh_details(section, name);
                }
            });
        });
        

    }

    function show_confirm_delete(name) {
        $("#delete-project").find("small").html(name);

        if ($("#delete-project").css("display") == "none") 
            $("#delete-project").modal("show");
        
        $("#delete-close-button").click(function() {
            $("#delete-project").modal("hide");
        });

        $("#delete-confirm-button").click(function() {
            $.ajax({
                type: "DELETE",
                url: "/project/" + name,
                success: function () {
                    $("#delete-project").modal("hide");
                    visit("project");
                }});
        });
    }

    function show_details(section, name) {
        refresh_details(section, name);
        $("#" + section + "-" + name + "-details").toggle("blind", function() {
            if($(this).css("display") == "none") {
                $.doTimeout("refresh-detail");
            }
        });

        $.doTimeout("refresh-detail", 10000, function(event, id) {
            refresh_details(section, name);
            return true;
        });
        
    }

    function show_log(name, build_id) {
        var build_log = $.ajax({url: "/log/" + name + "/" + build_id, dataType: "json", async: false}).responseText;
        $("#build-log-view").find("pre").html(build_log);
        
        if ($("#build-log-view").css("display") == "none") 
            $("#build-log-view").modal("show");
        
        $('#log-viewer')[0].scrollTop = $('#log-viewer')[0].scrollHeight;
        
        $("#build-log-view").bind("hide", function () {
            $.doTimeout('refresh-log');
        });

        $("#close-button").click(function() {
            $("#build-log-view").modal("hide");
        });

    }

    function visit(section) {
        $.ajax({
            url:"/" + section,
            method: "GET",
            dataType: "json",
            success: function(data) {
                var template = $.ajax({url:"/static/templates/" + section + ".html", async: false}).responseText;
                if (filter != "" && section == "project") {
                    filtered_data = [];
                    for (i=0; i<data.length; i++) {
                        if (data[i].name == filter) {
                            filtered_data.push(data[i]);
                        }
                    }   
                    data = filtered_data;
                }
                $("#content").html($.mustache(template, { items : data.sort(function(a, b) { 
                    if (a['name'] < b['name']) {
                        return -1;
                    } else {
                        return 1;
                    } 
                    if (a['name'] == b['name']) 
                        return 0;
                }) } ));
                $("#create").click(function() {
                        $("div[id="+ section +"-modal]").modal("show");
                });

                $("ul.nav").find("li").removeClass("active");
                $("li#" + section).addClass("active");

                switch(section) {
                    case 'group':
                            $(".edit").editInPlace({
                                callback : function(unused, enteredText) { 
                                    console.log($(this).attr("id") + " " + enteredText);
                                    $.ajax("/group/" + $(this).attr("group"), {
                                        type: "POST", 
                                        data: "edit=true&" + $(this).attr("id") + "=" + enteredText
                                    });
                                    return enteredText; 
                                }
                            });
                        break;

                    case 'project':
                        var groups_select = $.parseJSON($.ajax({url: "/group", dataType: "json", async: false}).responseText);
                        $("select#group_name").html("");
                        for(i=0, len=groups_select.length; i < len; i++) {
                            $("select#group_name").append("<option>" + groups_select[i].name + "</option>");
                        }

                        $("a[id^='show_']").each(function() {
                            $(this).click(function () { 
                                show_details('project', $(this).attr("id").split("_")[1]);
                            }); 
                        });

                        break;
                }

            } // sucess callback
        }); // ajax 

    }
   
    $('div[id*="-modal"]').each(function() {
        /* init forms */
        var section = $(this).attr("id").split("-")[0];
        
        $(this).modal({"backdrop": true});
        $(this).modal("hide");

        $(this).find("#create-" + section + "-button").click(function() { 
                    var data = $("div[id=" + section + "-modal]").find("form").serialize();
                    $.post("/"+ section, data, function() {
                        $("#create-" + section +"-form").find("input").each(
                            function () {
                                $(this).val("");
                            });
                        $("div[id="+ section +"-modal]").modal("hide"); 
                        visit(section);
                    });
                });
        
        $(this).find("#cancel-" + section + "-button").click(function() { $("div[id="+ section +"-modal]").modal("hide"); });
    });
                
    /*
    $("#build-log-view").dialog({
        autoOpen: false,
        height: 400,
        width: 470,
        modal: true,
    });
    */

    $("#build-log-view").modal({'backdrop': true});
    $("#build-log-view").modal("hide");
    
    $("ul.nav").find("li").each(function(){
        var menu_item = $(this);
        menu_item.click(function() {
            var menu_text = $(this);
            visit(menu_text.attr("id").toLowerCase()); 
        });
    });
    
    $('#create-group-form').ajaxForm(function() { 
            
    });

    $('#create-project-form').ajaxForm(function() { 
        
    });
    
    $('#search-form').ajaxForm();
    $('#search-form').submit(function () {
        filter = $(this).find("#search-projects").val();
        visit("project");
        show_details("project", filter);
        return false;
    });

    var project_list = $.parseJSON(
            $.ajax({
                url: "/project", 
                dataType: "json", 
                async: false}).responseText);

    var project_names = project_list.map(function(p) {return p['name'];});
    $('#search-projects').typeahead({'source': project_names});

    visit("project");
});
