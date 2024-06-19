document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("promptForm").addEventListener("submit", function (event) {
        event.preventDefault(); 
        
        var nombre = document.getElementById("nombre").value;
        var datasetEvaluar = document.getElementById("datasetEvaluar").value;
        var tecnicaUtilizada = document.getElementById("tecnicaUtilizada").value;
  
        var prompt = {
            nombre: nombre,
            datasetEvaluar: datasetEvaluar,
            tecnicaUtilizada: tecnicaUtilizada
        };
  
        fetch('/evaluador', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(prompt)
        })
        .then(response => {
            if (response.ok) {
                alert("Prompt guardado");
            } else {
                alert("Error en el guardado. Por favor, inténtalo de nuevo más tarde: " + response.statusText);
            }
        })
        .catch(error => {
            console.error('Error en la solicitud:', error);
            alert("Error en el guardado. Por favor, inténtalo de nuevo más tarde.");
        });
    });
});
