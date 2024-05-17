$(document).ready(function() {
    // Obtener los nombres de dataset mediante una solicitud AJAX al servidor
    $.ajax({
        url: '/obtener_dataset', // Ruta del endpoint para obtener los nombres de dataset
        type: 'GET',
        success: function(response) {
            // Manejar la respuesta del servidor
            var nombres = response.nombres;
            var selectDataset = $('#datasetEvaluar');
            // Agregar las opciones al desplegable
            nombres.forEach(function(nombre) {
                selectDataset.append('<option value="' + nombre + '">' + nombre + '</option>');
            });
        },
        error: function(xhr, status, error) {
            // Manejar errores de la solicitud
            console.error(error);
        }
    });
});