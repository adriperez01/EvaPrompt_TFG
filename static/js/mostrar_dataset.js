$(document).ready(function() {
    $('#previewButton').click(function() {
        const fileInput = document.getElementById('datasetFile');
        const file = fileInput.files[0];
        const columnaEvaluar = $('#columnaEvaluar').val();
        const columnaAsociada = $('#columnaAsociada').val();

        if (!columnaEvaluar || !columnaAsociada) {
            alert('Por favor, selecciona las columnas a evaluar y asociada.');
            return;
        }

        if (file) {
            Papa.parse(file, {
                header: true,
                skipEmptyLines: true,
                complete: function(results) {
                    const data = results.data;
                    actualizarTabla(data, columnaEvaluar, columnaAsociada);
                    $('#previewModal').modal('show');
                },
                error: function(error) {
                    console.error('Error al leer el archivo CSV:', error);
                    alert('Error al leer el archivo CSV. Por favor, verifica el archivo e intenta nuevamente.');
                }
            });
        } else {
            alert('Por favor, selecciona un archivo CSV para previsualizar.');
        }
    });
    
});

function actualizarTabla(dataset, columnaEvaluar, columnaAsociada) {
    console.log('Actualizando tabla con los siguientes datos:', dataset);
    console.log(columnaAsociada);
    console.log(columnaEvaluar);
    var tbody = $('#previewModal').find('tbody');
    tbody.empty();

    if (Array.isArray(dataset) && dataset.length > 0 && typeof dataset[0] === 'object' &&
        columnaEvaluar in dataset[0] && columnaAsociada in dataset[0]) {
        dataset.forEach(function(fila) {
            var tr = $('<tr>');
            var tdEvaluar = $('<td>').text(fila[columnaEvaluar]);
            var tdAsociada = $('<td>').text(fila[columnaAsociada]);
            tr.append(tdEvaluar, tdAsociada);
            tbody.append(tr);
        });

        var thead = $('#previewModal').find('thead');
        thead.empty();
        var tr = $('<tr>');
        var thEvaluar = $('<th>').text(columnaEvaluar);
        var thAsociada = $('<th>').text(columnaAsociada);
        tr.append(thEvaluar, thAsociada);
        thead.append(tr);
    } else {
        console.error('El dataset no está en el formato esperado o las columnas seleccionadas no existen.');
    }
}
