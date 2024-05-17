document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Evitar que el formulario se envíe normalmente

    var formData = new FormData(this); // Obtener los datos del formulario

    fetch('/login', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            // Redirigir al usuario a una página de dashboard, por ejemplo
            window.location.href = '/dashboard';
        } else {
            response.json().then(data => {
                // Mostrar el mensaje de error en un cuadro rojo dentro del formulario
                var errorContainer = document.getElementById('error-container');
                if (errorContainer) {
                    errorContainer.innerHTML = `<div class="alert alert-danger" role="alert">${data.message}</div>`;
                }
            });
        }
    })
    .catch(error => {
        console.error('Error al realizar la solicitud:', error);
    });
});
