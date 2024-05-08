$(document).ready(function() {

    $('#datasetFile').change(function() {
        // Llamar a la función para cargar los datos del archivo seleccionado
        cargarDatos();
    });


function cargarDatos(){
     // Crear un objeto FormData
    var formData = new FormData();

    // Agregar el archivo seleccionado al FormData
    var fileInput = $('#datasetFile')[0];
    formData.append('file', fileInput.files[0]);
    $.ajax({
            url: '/upload_dataset',
            type: 'POST',
            data: formData,
            processData: false,  // Evitar que jQuery procese los datos
            contentType: false,  // Evitar que jQuery establezca automáticamente el tipo de contenido
            success: function(response) {
                // Manejar la respuesta del servidor
                cargarColumnas(response.columnas);                        
            },
            error: function(xhr, status, error) {
                // Manejar errores de la solicitud
                console.error(error);
            }
        });
}    
// Función para cargar las columnas del dataset en los desplegables
function cargarColumnas(columnas) {
    var selectColumnaEvaluar = $('#columnaEvaluar');
    var selectColumnaAsociada = $('#columnaAsociada');

    // Limpiar los desplegables
    selectColumnaEvaluar.empty();
    selectColumnaAsociada.empty();

    // Verificar si columnas es un array antes de intentar iterar sobre él
    if (Array.isArray(columnas)) {
        // Agregar las columnas como opciones en los desplegables
        columnas.forEach(function(columna) {
            selectColumnaEvaluar.append('<option value="' + columna + '">' + columna + '</option>');
            selectColumnaAsociada.append('<option value="' + columna + '">' + columna + '</option>');
        });
    } else {
        console.error('El objeto de columnas no es un array:', columnas);
    }
}


    // Función para manejar el envío del formulario
    $('#uploadForm').submit(function(event) {
        // Evitar el envío del formulario por defecto
        event.preventDefault();

        // Crear un objeto FormData
        var formData = new FormData();

        // Agregar el archivo seleccionado al FormData
        var fileInput = $('#datasetFile')[0];
        formData.append('file', fileInput.files[0]);

        // Agregar el valor de la columna seleccionada a evaluar al FormData
        var columnaEvaluar = $('#columnaEvaluar').val();
        formData.append('columnaEvaluar', columnaEvaluar);

        // Agregar el valor de la columna seleccionada asociada al FormData
        var columnaAsociada = $('#columnaAsociada').val();
        formData.append('columnaAsociada', columnaAsociada);

        // Enviar los datos al servidor
        $.ajax({
            url: '/upload_dataset',
            type: 'POST',
            data: formData,
            processData: false,  // Evitar que jQuery procese los datos
            contentType: false,  // Evitar que jQuery establezca automáticamente el tipo de contenido
            success: function(response) {
                // Manejar la respuesta del servidor
                console.log(response);
                // Llamar a la función para actualizar la tabla de previsualización con los datos del dataset
                actualizarTabla(response.dataset, columnaEvaluar, columnaAsociada);
            },
            error: function(xhr, status, error) {
                // Manejar errores de la solicitud
                console.error(error);
            }
        });
    });

});