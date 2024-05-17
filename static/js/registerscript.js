document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("registro").addEventListener("submit", function (event) {
        event.preventDefault(); // Evitar el envío por defecto del formulario
        
        var nombre = document.getElementById("nombre").value;
        var correo = document.getElementById("correo_electronico").value;
        var contrasena = document.getElementById("contrasena").value;
        var confirmarContrasena = document.getElementById("confirmarContrasena").value;

        if (contrasena !== confirmarContrasena) {
            displayError("Las contraseñas no coinciden");
            return;
        }

        var usuario = {
            nombre: nombre,
            correo: correo,
            contrasena: contrasena
        };

        fetch('/registro', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(usuario)
        })
        .then(response => {
            if (response.ok) {
                window.location.href = '/login';
            } else if (response.status === 409) { // Error de correo ya registrado
                displayError("El correo electrónico ya está registrado");
            } else {
                alert("Error en el registro. Por favor, inténtalo de nuevo más tarde: " + response.statusText);
            }
        })
        .catch(error => {
            console.error('Error en la solicitud:', error);
            displayError("Error en el registro. Por favor, inténtalo de nuevo más tarde.");
        });
    });

    function displayError(message) {
        var errorContainer = document.getElementById("error-container");
        errorContainer.innerHTML = `<div class="alert alert-danger" role="alert">${message}</div>`;
    }
});
