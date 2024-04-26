$(function () {
    // se utiliza para las peticiones ajax con jquery
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
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