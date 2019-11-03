$(document).ready(function(){
    // $('.form-group').removeClass('row');
    var menu = $(".cont_menu_lateral");
    var menu_in = $("#event_menu_in");
    var menu_out = $("#event_menu_out");
    var ham_button = $(".menu-icon");
    out = true;
    var cont_contenedor = $("#cont_content");
    var little = false;
    var len = 0;

    $(document).on('click', '.browse', function(){
        var file = $(this).parent().parent().parent().find('.file');
        file.trigger('click');
    });
    $(document).on('change', '.file', function(){
        $(this).parent().find('.form-control').val($(this).val().replace(/C:\\fakepath\\/i, ''));
    });

    if("#estimate_appear"){
        var boton_es = $("#estimate_appear");
        var boton_gen = $("#generator_appear");
        var estimacion = $(".cont_estimacion")[0]
        var generador = $(".cont_generator")[0]
        var print = $("#print_es");
        var ctrl = 1;

        boton_es.on("click", function(){
            ctrl=0;
            estimacion.style.display = "block";
            generador.style.display = "none";
            boton_es[0].classList.add("active");
            boton_gen[0].classList.remove("active");
        });

        boton_gen.on("click", function(){
            ctrl=1;
            estimacion.style.display = "none";
            generador.style.display = "block";
            boton_es[0].classList.remove("active");
            boton_gen[0].classList.add("active");
        });

        print.on("click", function(){
            var win;
            var url = window.location.href
            url = url.replace('detalle', 'pdf');
            url = url.replace('#', '');
            url = url.replace('/arriba', '');
            url = url.replace('/abajo', '');
            if(ctrl!=0){
                url = url.replace('estimacion', 'generador');
            } else {
                url = url.replace('generador', 'estimacion');
            }
            win = window.open(url, '_blank');
            win.focus();
        });
    }

    var intcomma = function(value) {
        // inspired by django.contrib.humanize.intcomma, thanks to @banterabilitybanterability
        var origValue = String(value);
        var newValue = origValue.replace(/^(-?\d+)(\d{3})/, '$1,$2');
        if (origValue == newValue){
            return newValue;
        } else {
            return intcomma(newValue);
        }
    };
    
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

    ham_button.on("click", function(){
        if(out){
            menu[0].classList.add("disp_none");
            cont_contenedor.addClass("blur");
            out = false;
        } else {
            menu[0].classList.remove("disp_none");
            cont_contenedor.removeClass("blur");
            out = true;
        }
    });

    $(window).on("resize", function(){
        if(window.innerWidth < 600){
            ajustarContenido(1);
            menu_out.click();
            menu_in[0].style.display = "none";
        } else if (window.innerWidth >= 600 && !little) {
            cont_contenedor.removeClass("blur");
            if(!out){
                ham_button.click()
            }
            menu_in[0].style.display = "block";
            ajustarContenido(2);
        }
    });
    if(window.innerWidth < 600){
        menu_in[0].style.display = "none";
        ajustarContenido(1);
    } else if (window.innerWidth >= 600) {
        ajustarContenido(2);
    }

    if($("#cont_est_danger")){
        let delete_est = $(".anchor_est_delete");
        let msj = $("#cont_est_danger")[0];
        delete_est.on("click", function(target){
            let element = target.target;
            let url = url_for_list+"eliminar/"+element.getAttribute("data-model")+"/"+element.getAttribute("data-id").split(",").join("")+"/";
            $.ajax({
                url: url,
                type: 'GET',
                success: function(response){
                    msj.style.display = "block";
                    msj.innerHTML = response;
                    var f_data = $('#delete_form').serialize();
                    $("#button_cancel").on("click", function(target){
                        target.preventDefault();
                        msj.style.display = "none";
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
                },
            });
        });
    }

    if($(".div_list")){
        var div_list = $(".div_list");
        var delete_link = $(".anchor_delete");
        var mensaje = $("#cont_danger")[0];

        delete_link.on("click", function(target){
            mensaje.innerHTML = "";
            target.preventDefault();
            var element = target.target;
            var url = url_for_list+"eliminar/"+element.getAttribute("data-model")+"/"+element.getAttribute("data-id").split(",").join("")+"/";
            var pos = element.parentElement.getBoundingClientRect()
            for(i=0; i<div_list.length; i++){
                if(element.parentElement != div_list[i]){
                    div_list[i].classList.remove("border_danger");
                    div_list[i].classList.add("border_normal");
                }
            }
            mensaje.style.top = window.scrollY+pos.y+"px";
            mensaje.style.left = pos.x+"px";
            mensaje.style.display = "block";
            element.parentElement.classList.remove("border_normal");
            element.parentElement.classList.add("border_danger");
            $(window).on("resize", function(){
                pos = element.parentElement.getBoundingClientRect()
                mensaje.style.top = window.scrollY+pos.y+"px";
                mensaje.style.left = pos.x+"px";
            });
            $(window).on("scroll", function(){
                pos = element.parentElement.getBoundingClientRect()
                mensaje.style.top = window.scrollY+pos.y+"px";
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
    if($(".form-group > label:contains('Image')")){
        ocultar_elementos();
        $(".add-form").on("click", function(){
            ocultar_elementos();
        });
        function ocultar_elementos(){
            $(".form-group > label:contains('Image')").hide();
            $("label:contains('Eliminar')").parent().hide();
        }
        $(document).on("click", ".remove_ver_div", function(event){
            let ev = event.target;
            ev.closest(".remove_ver_div").nextSibling.nextSibling.children[0].children[0].click();
            ev.closest(".remove_ver_div").parentElement.classList.toggle("background_ver_eliminar");        
        });
        $(document).on("click", ".remove_img_span", function(event){
            let ev = event.target;
            ev.closest(".form-group").nextSibling.nextSibling.nextSibling.nextSibling.children[0].children[0].click();
            try {
                $(ev).parent().next().find(".custom-file-input")[0].classList.toggle("is-invalid");
                $(ev).parent().prev()[0].classList.toggle("appear");
                ev.classList.toggle("span_eliminar");
            } catch (err) {
                ev = ev.parentNode;
                $(ev).parent().next().find(".custom-file-input")[0].classList.toggle("is-invalid");
                $(ev).parent().prev()[0].classList.toggle("appear");
                ev.classList.toggle("span_eliminar");
            }
            
        });
        $(document).on('change', '.custom-file-input', function(){
            $(this).parent().find(".custom-file-label")[0].innerText = $(this).val().replace(/C:\\fakepath\\/i, '');
        });
    }
    if($("#select2-id_cliente-container").length && $("#select2-id_sitio-container").length){
        $("#id_cliente").on("change", function (){
            if($("#select2-id_cliente-container")[0].childNodes[0].nodeName != "SPAN"){
                $("#select2-id_sitio-container")[0].parentNode.parentNode.parentNode.parentNode.style.display = "block";
            } else {
                $("#select2-id_sitio-container")[0].parentNode.parentNode.parentNode.parentNode.style.display = "none";
            }
        });
        if($("#select2-id_cliente-container")[0].childNodes[0].nodeName == "SPAN"){
            $("#select2-id_sitio-container")[0].parentNode.parentNode.parentNode.parentNode.style.display = "none";
        }
    }
    if($(".llamar-subestimacion").length != null){
        $(".llamar-subestimacion").on("click", function(evt){
            var url = evt.target.dataset['url'];
            var position = parseInt(evt.target.dataset['position']);
            //$(".clicked").parent().parent().parent().addClass("trclickeado");
            if($(".clicked").length > 0 && evt.target == $(".clicked")[0]){
                var position = parseInt($(".clicked")[0].dataset['position'])+1;
                var row = $("#subcontrato-table")[0].deleteRow(position);
                $(evt.target).removeClass("clicked");
                $(evt.target).removeClass("oi-chevron-bottom");
                $(evt.target).addClass("oi-chevron-right");
            } else if($(".clicked").length > 0){
                    $($(".clicked")[0]).removeClass("oi-chevron-bottom");
                    $($(".clicked")[0]).addClass("oi-chevron-right");
                    var pos_1 = parseInt($(".clicked")[0].dataset['position'])+1;
                    var row = $("#subcontrato-table")[0].deleteRow(pos_1);
                    $($(".clicked")[0]).removeClass("clicked");


                    $(evt.target).addClass("clicked");
                    var position = parseInt($(".clicked")[0].dataset['position'])+1;
                    $.ajax({
                    url: url,
                    type: 'GET',
                    success: function(response){
                        var indice = position;
                        var row = $("#subcontrato-table")[0].insertRow(indice);
                        var text = "<td colspan='6' id='subestimacioncontainer'><div>"+ response +"</div></td>";
                        row.innerHTML = text;
                    },
                    });
                    $($(".clicked")[0]).removeClass("oi-chevron-right");
                    $($(".clicked")[0]).addClass("oi-chevron-bottom");
            } else {
                $.ajax({
                    url: url,
                    type: 'GET',
                    success: function(response){
                        var indice = position+1;
                        var row = $("#subcontrato-table")[0].insertRow(indice);
                        var text = "<td colspan='6' id='subestimacioncontainer'><div>"+ response +"</div></td>";
                        row.innerHTML = text;
                    },
                });
                $(evt.target).addClass("clicked");
                $($(".clicked")[0]).removeClass("oi-chevron-right");
                $($(".clicked")[0]).addClass("oi-chevron-bottom");
            }
        });
    }
});


