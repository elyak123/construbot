$(document).ready(function(){
  let current = $(".calcular-mul")[0];
  let button = $(".calcular_cantidad");
  button.on("click", function n(ev){
    calcular(ev);
  });
  function calcular(ev){
    ev.preventDefault();
    let source = ev.target.parentElement.parentElement;
    let container = source.parentElement;
    let elements = $(container).find(".vertices");
    let estimado = 0;
    for(let i = 0; i < elements.length; i++){
      let mult = 1;
      for(let j = 2; j < 6; j++){
        mult *= elements[i].children[j].children[0].children[1].value;
      }
      estimado+=mult;
    }
    $(container).find("[placeholder='Cantidad estimada']")[0].value = estimado.toFixed(2);
  }
  $('textarea').each(function () {
    this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
  }).on('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
  });
});
