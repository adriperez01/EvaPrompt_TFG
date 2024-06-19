$(document).ready(function() {

    $.ajax({
        url: '/obtener_dataset', 
        type: 'GET',
        success: function(response) {
            
            var nombres = response.nombres;
            var selectDataset = $('#datasetEvaluar');
            
            nombres.forEach(function(nombre) {
                selectDataset.append('<option value="' + nombre + '">' + nombre + '</option>');
            });
        },
        error: function(xhr, status, error) {
            
            console.error(error);
        }
    });
});