$(document).ready(function() {

    $('#datasetFile').change(function() {
        // Llamar a la función para cargar los datos del archivo seleccionado
        cargarDatos();
    });


function cargarDatos(){
     
    var formData = new FormData();

    var fileInput = $('#datasetFile')[0];
    formData.append('file', fileInput.files[0]);
    $.ajax({
            url: '/upload_dataset',
            type: 'POST',
            data: formData,
            processData: false,  
            contentType: false,  
            success: function(response) {
                
                cargarColumnas(response.columnas);                        
            },
            error: function(xhr, status, error) {
                
                console.error(error);
            }
        });
}    

function cargarColumnas(columnas) {
    var selectColumnaEvaluar = $('#columnaEvaluar');
    var selectColumnaAsociada = $('#columnaAsociada');

    
    selectColumnaEvaluar.empty();
    selectColumnaAsociada.empty();

    
    if (Array.isArray(columnas)) {
        
        columnas.forEach(function(columna) {
            selectColumnaEvaluar.append('<option value="' + columna + '">' + columna + '</option>');
            selectColumnaAsociada.append('<option value="' + columna + '">' + columna + '</option>');
        });
    } else {
        console.error('El objeto de columnas no es un array:', columnas);
    }
}


    
    $('#uploadForm').submit(function(event) {
        
        event.preventDefault();

        
        var formData = new FormData();

        
        var fileInput = $('#datasetFile')[0];
        formData.append('file', fileInput.files[0]);
        
        var nombre = $('#nombre').val();
        formData.append('nombre', nombre);
        
        var columnaEvaluar = $('#columnaEvaluar').val();
        formData.append('columnaEvaluar', columnaEvaluar);
        
        var columnaAsociada = $('#columnaAsociada').val();
        formData.append('columnaAsociada', columnaAsociada);

       
        $.ajax({
            url: '/upload_dataset',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                toastr.success('Dataset subido correctamente.');
            },
            error: function(error) {
                toastr.error('Error al subir el dataset. Por favor, intenta nuevamente..');
            }
        });
    });

});