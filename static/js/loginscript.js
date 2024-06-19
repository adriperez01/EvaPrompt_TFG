document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); 
    var formData = new FormData(this); 

    fetch('/login', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            
            window.location.href = '/dashboard';
        } else {
            response.json().then(data => {
                
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
