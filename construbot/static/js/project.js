/* Project specific Javascript goes here. */

/*
Formatting hack to get around crispy-forms unfortunate hardcoding
in helpers.FormHelper:

    if template_pack == 'bootstrap4':
        grid_colum_matcher = re.compile('\w*col-(xs|sm|md|lg|xl)-\d+\w*')
        using_grid_layout = (grid_colum_matcher.match(self.label_class) or
                             grid_colum_matcher.match(self.field_class))
        if using_grid_layout:
            items['using_grid_layout'] = True

Issues with the above approach:

1. Fragile: Assumes Bootstrap 4's API doesn't change (it does)
2. Unforgiving: Doesn't allow for any variation in template design
3. Really Unforgiving: No way to override this behavior
4. Undocumented: No mention in the documentation, or it's too hard for me to find
*/
$(document).ready(function(){
	// $('.form-group').removeClass('row');
    var menu = $(".cont_menu_lateral");
    var menu_in = $("#event_menu_in");
    var menu_out = $("#event_menu_out");
    var cont_contenedor = $("#cont_content");
    var little = false;

    function OnchangeEventHandler(event) {
        if(event.target.value){
            $.ajax({
                url:'/users/company-change/' + event.target.value + '/',
                type: 'GET',
                success: function(response){
                    window.location.reload();
                },
            });
        } 
    }
    document.querySelector('#company_select').onchange=OnchangeEventHandler

    function hideMenu(){
        menu[0].style.display = "none";
        cont_contenedor.removeClass("content_with_little_sidebar");
        cont_contenedor.removeClass("content_with_sidebar");
        cont_contenedor.addClass("content_without_sidebar");
    }

    menu_in.on("click", function(){
        for(var i = 0; i<$(".menuSign").length; i++){
            $(".menuSign")[i].style.display = "none";
        }
        for(var i = 0; i<$(".list_subsubmenu").length; i++){
            $(".list_subsubmenu")[i].style["margin-left"] = "55px";
        }
        menu[0].style.width = "55px";
        menu_in[0].style.display = "none";
        menu_out[0].style.display = "block";
        cont_contenedor.removeClass("content_with_sidebar");
        cont_contenedor.addClass("content_with_little_sidebar");
        little = true;

    });

    menu_out.on("click", function(){
        for(var i = 0; i<$(".menuSign").length; i++){
            $(".menuSign")[i].style.display = "initial";
        }
        for(var i = 0; i<$(".list_subsubmenu").length; i++){
            $(".list_subsubmenu")[i].style["margin-left"] = "200px";
        }
        menu[0].style.width = "200px";
        menu_in[0].style.display = "block";
        menu_out[0].style.display = "none";
        cont_contenedor.removeClass("content_with_little_sidebar");
        cont_contenedor.addClass("content_with_sidebar");
        little = false;
    });

    $(window).on("resize", function(){
        if(window.innerWidth < 600 && window.innerWidth > 375 && !little){
            menu_in.click();
        }
        if(window.innerWidth < 375){
            hideMenu();
        }
    });
    if(window.innerWidth < 600 && !little){
        menu_in.click();
    }
    if(window.innerWidth < 375){
        hideMenu();
    }
    $(window).on("load", function(){
        debugger;
    });
});