$(document).ready(function(){
  let button = $(".calcular_cantidad");
  button.on("click", function n(ev){
    calcular(ev);
  });
  function calcular(ev){
    ev.preventDefault();
    let source = ev.target.parentElement.parentElement;
    let field = source.children[1].children[0].children[1];
    let values = source.parentElement;
    let v1 = parseFloat(values.children[0].children[0].children[1].value);
    let v2 = parseFloat(values.children[1].children[0].children[1].value);
    let v3 = parseFloat(values.children[2].children[0].children[1].value);
    field.value = (v1*v2*v3).toFixed(2);
  }
  $('textarea').each(function () {
    this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
  }).on('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
  });
});
