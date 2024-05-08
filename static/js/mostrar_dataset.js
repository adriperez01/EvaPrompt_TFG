function actualizarTabla(dataset, columnaEvaluar, columnaAsociada) {
    console.log('Actualizando tabla con los siguientes datos:', dataset);

    // Limpiar el contenido actual de la tabla
    var tbody = $('#datasetPreview').find('tbody');
    tbody.empty();

    // Verificar si el dataset es un array de objetos y si las columnas existen en los objetos
    if (Array.isArray(dataset) && dataset.length > 0 && typeof dataset[0] === 'object' &&
        columnaEvaluar in dataset[0] && columnaAsociada in dataset[0]) {
        // Iterar sobre el dataset y agregar filas a la tabla
        dataset.forEach(function(fila) {
            var tr = $('<tr>');
            // Agregar celdas para las columnas seleccionadas
            var tdEvaluar = $('<td>').text(fila[columnaEvaluar]);
            var tdAsociada = $('<td>').text(fila[columnaAsociada]);
            tr.append(tdEvaluar, tdAsociada);
            tbody.append(tr); // Agregar la fila a la tabla
        });

        // Actualizar el encabezado de la tabla con los nombres de las columnas seleccionadas
        var thead = $('#datasetPreview').find('thead');
        thead.empty(); // Limpiar el contenido actual del encabezado de la tabla
        var tr = $('<tr>');
        var thEvaluar = $('<th>').text(columnaEvaluar);
        var thAsociada = $('<th>').text(columnaAsociada);
        tr.append(thEvaluar, thAsociada);
        thead.append(tr); // Agregar la fila al encabezado de la tabla
    } else {
        console.error('El dataset no está en el formato esperado o las columnas seleccionadas no existen.');
    }
    
}
