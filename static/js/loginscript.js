document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Evitar que el formulario se envíe normalmente

    var formData = new FormData(this); // Obtener los datos del formulario

    fetch('/login', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            alert('Inicio de sesión exitoso');
            // Redirigir al usuario a una página de dashboard, por ejemplo
            window.location.href = '/dashboard';
        } else {
            response.json().then(data => {
                alert('Error: ' + data.message);
            });
        }
    })
    .catch(error => {
        console.error('Error al realizar la solicitud:', error);
    });
});