$(function () {
  // $("#tblUsuarios").DataTable();
  // $("#tblElementosDevolutivos").DataTable();
  $("#fileFoto").on("change", validarImagen);
  $("#fileFoto").on("change", mostrarImagen);
});

/**
 * Valida la extensión y el tamaño de una imagen seleccionada en un input de tipo "file".
 * Muestra mensajes de advertencia con SweetAlert en caso de una extensión incorrecta o un tamaño excesivo.
 * @param {Event} evt - El evento del input "file" que desencadena la función.
 */
function validarImagen(evt) {
  let files = evt.target.files;
  var fileName = files[0].name;
  var fileSize = files[0].size;
  let extension = fileName.split(".").pop();
  extension = extension.toLowerCase();
  if (extension !== "jpg" && extension !== "png") {
    Swal.fire(
      "Cargar Imagen",
      "La imagen debe tener una extensión JPG o PNG",
      "warning"
    );
    $("#fileFoto").val("");
    $("#fileFoto").focus();
  } else if (fileSize > 900000) {
    Swal.fire(
      "Cargar Imagen",
      "La imagen NO puede superar los 900K",
      "warning"
    );
    $("#fileFoto").val("");
    $("#fileFoto").focus();
  }
}

/**
 * Muestra una vista previa de la imagen seleccionada en un input de tipo "file" en elementos de imagen HTML.
 * @param {Event} evt - El evento del input "file" que desencadena la función.
 */
function mostrarImagen(evt) {
  const archivos = evt.target.files;
  const archivo = archivos[0];
  const url = URL.createObjectURL(archivo);

  $("#imagenUsuario").attr("src", url);
  $("#imagenProducto").attr("src", url);
}


document.addEventListener('DOMContentLoaded', function () {
  // Obtén el elemento select
  var cbMetodoAbono = document.getElementById('cbMetodoAbono');

  // Obtén los elementos que deseas mostrar u ocultar
  var bancolombiaInfo = document.getElementById('bancolombiaInfo');
  var daviplataInfo = document.getElementById('daviplataInfo');
  var nequiInfo = document.getElementById('nequiInfo');

  // Agrega un controlador de eventos para el cambio en el select
  cbMetodoAbono.addEventListener('change', function () {
      // Oculta todos los elementos de información
      bancolombiaInfo.style.display = 'none';
      daviplataInfo.style.display = 'none';
      nequiInfo.style.display = 'none';

      // Muestra el elemento de información correspondiente a la opción seleccionada
      var selectedOption = cbMetodoAbono.options[cbMetodoAbono.selectedIndex].value;
      if (selectedOption === '1') {
          bancolombiaInfo.style.display = 'block';
      } else if (selectedOption === '2') {
          daviplataInfo.style.display = 'block';
      } else if (selectedOption === '3') {
        nequiInfo.style.display = 'block';
      }
  });
});