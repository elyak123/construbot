$(document).ready(function(){
  var current = $(".calcular-mul")[0];
  var button = $(".calcular_cantidad");
  button.on("click", function n(ev){
    calcular(ev);
  });
  function calcular(ev){
    ev.preventDefault();
    var source = ev.target.parentElement.parentElement;
    var container = source.parentElement;
    var elements = $(container).find(".vertices");
    var estimado = 0;
    for(var i = 0; i < elements.length; i++){
      var mult = 1;
      mult*=$(elements[i]).find(".alto").children()[0].value;
      mult*=$(elements[i]).find(".ancho").children()[0].value;
      mult*=$(elements[i]).find(".largo").children()[0].value;
      mult*=$(elements[i]).find(".piezas").children()[0].value;
      estimado+=mult;
    }
    $(container).find("[placeholder='Cantidad estimada']")[0].value = estimado.toFixed(2);
  }
  function textarea(){
    $('textarea').each(function () {
      this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
    }).on('input', function () {
      this.style.height = 'auto';
      this.style.height = (this.scrollHeight) + 'px';
    });
  }
  textarea();
});
