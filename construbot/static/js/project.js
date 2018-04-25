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
    var len = 0;

    if($(".icon_right")){
        $(".icon_right").on("click", function(){
            $(".icon_right-up")[0].style.display = "initial";
            $(".icon_right")[0].style.display = "none";
            $.ajax({
                url: "/proyectos/contrato/catalogo-list/" + document.URL.slice(-2)[0] + "/",
                success: function(result){
                    $(".cont_result")[0].style.display = "block";
                    result = result.conceptos;
                    len = result.length;
                    if(len>0){
                        $(".table_results")[0].style.display = "inline-table";
                        for(i=1; i<=len; i++){
                            var row = $(".table_results")[0].insertRow(i);
                            var row_content = "<td>"+result[i-1]["code"]+"</td><td>"+result[i-1]["concept_text"]+"</td><td>"+result[i-1]["unit"]+"</td><td>"+result[i-1]["cuantity"]+"</td><td>"+result[i-1]["unit_price"]+"</td>";
                            row.innerHTML = row_content;
                        }
                    } else {
                        $(".cont_message_no_result")[0].style.display = "block";
                    }
                }
            });
        });

        $(".icon_right-up").on("click", function(){
            $(".icon_right-up")[0].style.display = "none";
            $(".icon_right")[0].style.display = "initial";
            if(len>0){
                $(".cont_result")[0].style.display = "none";
                $(".table_results")[0].style.display = "none";
                for(i=0; i<len; i++){
                    $(".table_results")[0].deleteRow(1);
                }
            } else {
                $(".cont_message_no_result")[0].style.display = "none";
            }
        });
    }

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

    function ajustarContenido(arg){
        if(arg==1){
            cont_contenedor.removeClass("content_with_little_sidebar");
            cont_contenedor.removeClass("content_with_sidebar");
            cont_contenedor.addClass("content_without_sidebar");
        } else if (arg==2 && little){
            cont_contenedor.addClass("content_with_little_sidebar");
            cont_contenedor.removeClass("content_with_sidebar");
            cont_contenedor.removeClass("content_without_sidebar");
        } else if (arg==2 && !little){
            cont_contenedor.removeClass("content_with_little_sidebar");
            cont_contenedor.addClass("content_with_sidebar");
            cont_contenedor.removeClass("content_without_sidebar");
        }
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
            ajustarContenido(1);
        } else if (window.innerWidth >= 375) {
            ajustarContenido(2);
        }
    });
    if(window.innerWidth < 600 && !little){
        menu_in.click();
    }
    if(window.innerWidth < 375){
        ajustarContenido(1);
    } else if (window.innerWidth >= 375) {
        ajustarContenido(2);
    }

    if($(".div_list")){
        var div_list = $(".div_list");
        var delete_link = $(".anchor_delete");
        var mensaje = $("#cont_danger")[0];

        delete_link.on("click", function(target){
            var element = target.target;
            var url = "/proyectos/eliminar/"+element.getAttribute("data-model")+"/"+element.getAttribute("data-id")+"/";
            var pos = element.parentElement.getBoundingClientRect()
            for(i=0; i<div_list.length; i++){
                if(element.parentElement != div_list[i]){
                    div_list[i].classList.remove("border_danger");
                    div_list[i].classList.add("border_normal");
                }
            }
            mensaje.style.top = pos.y+"px";
            mensaje.style.left = pos.x+"px";
            mensaje.style.display = "block";
            element.parentElement.classList.remove("border_normal");
            element.parentElement.classList.add("border_danger");
            $(window).on("resize", function(){
                pos = this.element.parentElement.getBoundingClientRect()
                mensaje.style.top = pos.y+"px";
                mensaje.style.left = pos.x+"px";
            });
            $.ajax({
                url: url,
                type: 'GET',
                success: function(response){
                    mensaje.innerHTML = response;
                    habilitarBotones();
                },
            });
            function habilitarBotones(){
                var f_data = $('#delete_form').serialize();
                $("#button_cancel").on("click", function(target){
                    target.preventDefault();
                    element.parentElement.classList.add("border_normal");
                    element.parentElement.classList.remove("border_danger");
                    mensaje.style.display = "none";
                });
                $("#delete_form").submit(function(event){
                    event.preventDefault()
                    $.ajax({
                        type:"POST",
                        url: url,
                        data: f_data,
                        success: function(){
                            window.location.reload() 
                        }
                    });
                });
            }
        });
    }
});
