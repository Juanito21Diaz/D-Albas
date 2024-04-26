let productos = []
let detalleSolicitudPedidos = []
let totalAPagar = 0; 
$(function () {
    // se utiliza para las peticiones ajax con jquery
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    });

    $("#btnAgregarDetallePedido").click(function () {
        agregarDetallePedido();
    });

    $("#btnRegistrarPedido").click(function () {
        if (validarFechaHoraPedido()) {
            registroPedido();
        }
    });
});

/**
 * Obtiene el valor de una cookie específica en el navegador web.
 * Las cookies son fragmentos de información almacenados en el navegador del usuario.
 * @param {string} name - El nombre de la cookie que se desea obtener.
 * @returns {string|null} - El valor de la cookie si se encuentra, o null si la cookie no existe.
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Realiza el registro de un pedido mediante una petición AJAX a un servidor.
 * Los datos del pedido se obtienen de los elementos del formulario HTML y se envían al servidor.
 * Si los campos obligatorios no están completos, muestra una notificación de error.
 * @returns {void}
 */
function registroPedido() {
    var nombreCliente = $("#txtNombreCliente").val();
    var telefonoCliente = $("#txtTelefonoCliente").val();
    var fechaHoraPedido = $("#txtFechaHoraPedido").val();
    var metodoPago = $("#cbMetodoPago").val();
    var correoCliente = $("#txtCorreoCliente").val();

    if (!nombreCliente || !telefonoCliente || !fechaHoraPedido || !metodoPago || !correoCliente) {
        Swal.fire("Registro de Pedido", "Por favor, complete todos los campos obligatorios.", "info");
        return;
    }

    if (!validarCorreo(correoCliente)) {
        Swal.fire("Registro de Pedido", "Por favor, ingrese una dirección de correo electrónico válida.", "info");
        return;
    }

    var datos = {
        "nombreCliente": nombreCliente,
        "telefonoCliente" : telefonoCliente,
        "fechaHoraPedido" : fechaHoraPedido,
        "metodoPago" : metodoPago,
        "correoCliente" : correoCliente,
        "detalle": JSON.stringify(detalleSolicitudPedidos),
    };

    $.ajax({
        url: "/registrarPedidoAdmin/",
        data: datos,
        type: 'post',
        dataType: 'json',
        cache: false,
        success: function (resultado) {
            console.log(resultado);
            if (resultado.estado) {
                frmRegistrarPedido.reset();
                detalleSolicitudPedidos.length = 0;
                mostrarDatosTabla();
            }
            Swal.fire("Registro de Pedido", resultado.mensaje, "success");
            location.href = "/vistaRegistrarPedidoAdmin/";
        }
    });
}

/**
 * Agrega un detalle de pedido a la lista de detalles de solicitud de pedidos.
 * Los detalles se obtienen de los campos del formulario HTML y se validan antes de agregarlos.
 * Si el producto ya está agregado, muestra una notificación de error.
 * @returns {void}
 */
function agregarDetallePedido() {
    var cantidadProducto = $("#txtCantidadProducto").val();
    var precioProducto = $("#txtPrecioProducto").val();
    var cbProducto = $("#cbProducto").val();

    if (!cbProducto) {
        Swal.fire("Registro de Pedido", "Por favor, seleccione el producto que desea comprar.", "info");
        return;
    } else if (!cantidadProducto || !precioProducto) {
        Swal.fire("Registro de Pedido", "Por favor, ingrese la cantidad del productos que desea comprar.", "info");
        return;
    }

    const e = detalleSolicitudPedidos.find(producto => producto.idProducto == cbProducto);
    if (e == null) {
        const cantidad = parseInt(cantidadProducto);
        if (!isNaN(cantidad)) {
            const producto = {
                "idProducto": cbProducto,
                "cantidad": cantidad,
                "precio": precioProducto, 
            };
            detalleSolicitudPedidos.push(producto);
            frmDetalleSolicitud.reset();
            mostrarDatosTabla();
        } else {
            Swal.fire("Registro de Pedido", "La cantidad ingresada no es válida. Verifique", "info");
        }
    } else {
        Swal.fire("Registro de Pedido", "El producto seleccionado ya está agregado. Verifique", "info");
    }
}

/**
 * Actualiza y muestra los datos en una tabla HTML que representa los detalles del pedido.
 * Calcula el precio acumulado de cada producto y actualiza el total a pagar.
 * @returns {void}
 */
function mostrarDatosTabla() {
    let datos = "";
    totalAPagar = 0; 
    detalleSolicitudPedidos.forEach(entrada => {
        const E = productos.findIndex(producto => producto.idProducto  == entrada.idProducto);
        const cantidad = entrada.cantidad;
        const precioUnitario = productos[E].precioProducto;
        const precioAcumulado = cantidad * precioUnitario;
        totalAPagar += precioAcumulado; 
        datos += "<tr>";
        datos += "<td class='text-center'>" + productos[E].nombreProducto + "</td>";
        datos += "<td class='text-center'>" + "$" + precioUnitario + "</td>";
        datos += "<td class='text-center'>"  + "$" + precioAcumulado + "</td>";
        datos += "<td class='text-center'>" + cantidad + "</td>";
        datos += "</tr>";
    });
    $("#datosTablaPedidos").html(datos);
    $("#totalAPagar").text("Total: $" + totalAPagar);
}

/**
 * Carga información de productos en la lista de productos
 * @param {number} idProducto - ID del producto
 * @param {string} nombreProducto - Nombre del producto
 * @param {number} precioProducto - Precio del producto
 */
function cargarProductos(idProducto, nombreProducto, precioProducto) {
    const elemento = {
        "idProducto": idProducto,
        "nombreProducto": nombreProducto,
        "precioProducto": precioProducto,
    };
    productos.push(elemento);
}

/**
 * Valida si una dirección de correo electrónico tiene un formato válido.
 *
 * @param {string} correo - La dirección de correo electrónico que se va a validar.
 * @returns {boolean} True si la dirección de correo electrónico es válida, false en caso contrario.
 */
function validarCorreo(correo) {
    var expresionRegular = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return expresionRegular.test(correo);
}

/**
 * Valida si la fecha y hora del pedido cumplen con ciertas restricciones:
 * - Debe completarse el campo de fecha y hora.
 * - La fecha y hora ingresadas deben ser válidas y tener el formato correcto.
 * - Debe hacerse un pedido con al menos 7 días de antelación.
 * - No se pueden hacer pedidos los días domingos.
 * - Los pedidos solo se atienden entre las 8 AM y las 8 PM.
 * - Verifica si la fecha seleccionada es un día festivo en Colombia (usando la función esFestivo).
 * @returns {boolean} - Devuelve true si la fecha y hora son válidas y cumplen con las restricciones, 
 * false en caso contrario.
 */
function validarFechaHoraPedido() {
    const fechaHoraPedidoString = $("#txtFechaHoraPedido").val();

    if (!fechaHoraPedidoString) {
        Swal.fire("Registro de Pedido", "Por favor, complete todos los campos obligatorios.", "info");
        return false;
    }

    const fechaHoraPedido = new Date(fechaHoraPedidoString);

    if (isNaN(fechaHoraPedido.getTime())) {
        Swal.fire("Registro de Pedido", "La fecha y hora ingresadas no son válidas. Verifique el formato.", "info");
        return false;
    }

    const ahora = new Date();

    // Validación de mínimo 7 días de antelación
    const diferenciaDias = Math.floor((fechaHoraPedido - ahora) / (1000 * 60 * 60 * 24));
    if (diferenciaDias < 7) {
        Swal.fire("Registro de Pedido", "Se requiere un mínimo de 8 días de antelación para realizar el pedido.", "error");
        return false;
    }

    // Validación de días domingos
    const diaSemana = fechaHoraPedido.getDay();
    if (diaSemana === 0) {
        Swal.fire("Registro de Pedido", "No se atienden pedidos los días domingos.", "error");
        return false;
    }

    // Validación de horarios de atención (8 AM - 8 PM)
    const hora = fechaHoraPedido.getHours();
    if (hora < 8 || hora >= 20) {
        Swal.fire("Registro de Pedido", "Los pedidos solo se atienden de 8 AM a 8 PM.", "error");
        return false;
    }

    // Validación de festivos en Colombia (Asumiendo la función esFestivoColombia)
    if (esFestivo(fechaHoraPedido)) {
        Swal.fire("Registro de Pedido", "La fecha seleccionada es día festivo.", "error");
        return false;
    }

    return true; // La fecha y hora son válidas
}

/**
 * Verifica si una fecha específica es un día festivo en Colombia.
 * @param {Date} fecha - La fecha que se desea verificar si es un día festivo.
 * @returns {boolean} - Devuelve true si la fecha es un día festivo en Colombia, false en caso contrario.
 */
function esFestivo(fecha) {
    const year = fecha.getFullYear();
    const diasFestivos = obtenerDiasFestivos(year); 

    const fechaFormateada = fecha.toISOString().split("T")[0];

    return diasFestivos.includes(fechaFormateada);
}

/**
 * Obtiene una lista de días festivos en Colombia para un año específico.
 * @param {number} year - El año para el cual se desean obtener los días festivos.
 * @returns {string[]} - Un array de strings que representa las fechas de los días festivos en el formato "yyyy-mm-dd".
 */
function obtenerDiasFestivos(year) {
    const diasFestivos = [
        year + "-01-01", // Año Nuevo
        year + "-01-09", // Día de los Reyes Magos
        year + "-03-20", // Día de San José
        year + "-04-02", // Domingo de Ramos
        year + "-04-06", // Jueves Santo
        year + "-04-07", // Viernes Santo
        year + "-04-09", // Domingo de Resurrección
        year + "-05-01", // Día del Trabajo
        year + "-05-22", // Día de la Ascensión de Jesús
        year + "-06-12", // Corpus Christi
        year + "-06-19", // Sagrado corazón
        year + "-07-03", // San Pedro y San Pablo
        year + "-07-20", // Día de la Independencia de Colombia
        year + "-08-07", // Batalla de Boyacá
        year + "-08-21", // Asunción de la Virgen María
        year + "-10-16", // Día de la Raza
        year + "-11-06", // Día de todos los Santos
        year + "-11-13", // Independencia de Cartagena
        year + "-12-08", // Día de la Inmaculada Concepción
        year + "-12-25", // Navidad
    ];

    return diasFestivos;
}


// ESTAS FUNCIONES COMENTADAS SE PLANEA IMPLEMENTAR A FUTURO,
// YA QUE ES UNA MANERA MÁS AGIL DE VALIDAR LOS DÍAS FESTIVOS,
// Y SE HACER POR MEDIO DE UNA API
// 
// function formatDate(date) {
//     const year = date.getFullYear();
//     const month = String(date.getMonth() + 1).padStart(2, '0');
//     const day = String(date.getDate()).padStart(2, '0');
//     return `${year}-${month}-${day}`;
// }

// // Función para verificar si una fecha es festiva en Colombia
// function esFestivo(fecha) {
//     const year = fecha.getFullYear();
//     const fechaFormateada = formatDate(fecha);

//     // URL de la API para obtener los días festivos en Colombia
//     const url = `https://date.nager.at/api/v3/publicholidays/${year}/CO`;
    
//     return new Promise(function(resolve, reject) {
//         $.ajax({
//             url: url,
//             method: "GET",
//             dataType: "json",
//             success: function(response) {
//                 // Verifica si la fecha está en la lista de días festivos
//                 if (response.some(holiday => holiday.date === fechaFormateada)) {
//                     resolve(true);
//                 } else {
//                     resolve(false);
//                 }
//             },
//             error: function(error) {
//                 console.error("Error al obtener los días festivos desde la API", error);
//                 reject(error);
//             }
//         });
//     });
// }