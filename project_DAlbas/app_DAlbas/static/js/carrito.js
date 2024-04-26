//esto es solo cosas para que el ajax funcione y tal
$(function(){
    $.ajaxSetup({
        headers:{
            'X-CSRFToken':getCookie('csrftoken')
        }
    })
    
})

/**
 * Obtiene el valor de una cookie según el nombre especificado.
 * @param {string} name - El nombre de la cookie que se desea recuperar.
 * @returns {string|null} El valor de la cookie si existe, o null si no se encuentra.
 */
function getCookie(name){
    let cookieValue = null;
    if (document.cookie && document.cookie !== ''){
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0,name.length + 1) === (name + '=')){
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
            
        }
    }
    return cookieValue;
}

/**
 * Envía un ID de producto a través de una solicitud AJAX a una vista específica.
 * Muestra un mensaje de confirmación usando SweetAlert cuando se completa la solicitud.
 * @param {string} id - El ID del producto que se va a enviar en la solicitud.
 */
function mandarId(id){
    var datos = {
        "idProducto": id,
    }  
    $.ajax({
        url: "/vistaCarritoCompras/",
        data: datos,
        type: 'post',
        dataType: 'json',
        cache: false,
        success: function(resultado){
            console.log(resultado);
            Swal.fire("Registro de Solicitud",resultado.mensaje,"success")
        }
    })
}

/**
 * Elimina un producto del carrito de compras.
 * Realiza una solicitud AJAX para eliminar el producto en el backend y elimina la fila correspondiente de la tabla.
 * Muestra un mensaje de confirmación usando SweetAlert cuando se completa la solicitud.
 * @param {Event} event - El evento de clic que desencadena la función, generalmente un botón de eliminación de producto.
 */
function eliminarProducto(event) {
    // Obtiene el elemento TR que contiene toda la información del producto
    const filaProducto = event.target.closest('tr');
    
    // Obtiene el ID del producto
    const idProducto = filaProducto.querySelector('td').textContent;
    
    // Elimina el producto del carrito en el backend (haciendo una llamada AJAX a la vista "eliminarProductoCarrito")
    $.ajax({
        url: "/eliminarProductoCarrito/",
        data: {idProducto: idProducto},
        type: 'post',
        dataType: 'json',
        cache: false,
        success: function(resultado) {
            console.log(resultado);
            Swal.fire("Eliminación de Producto", resultado.mensaje, "success");
            
            // Elimina la fila del producto de la tabla
            filaProducto.remove();
        }
    });
}
