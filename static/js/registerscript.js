document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("registro").addEventListener("submit", function (event) {
      event.preventDefault(); // Evitar el envío por defecto del formulario
      
      var nombre = document.getElementById("nombre").value;
      var correo = document.getElementById("correo_electronico").value;
      var contrasena = document.getElementById("contrasena").value;
      var confirmarContrasena = document.getElementById("confirmarContrasena").value;

      if (contrasena !== confirmarContrasena) {
          alert("Las contraseñas no coinciden");
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
              alert("Registro exitoso");
              window.location.href = '/login';
          } else {
              alert("Error en el registro. Por favor, inténtalo de nuevo más tarde: " + response.statusText);
          }
      })
      .catch(error => {
          console.error('Error en la solicitud:', error);
          alert("Error en el registro. Por favor, inténtalo de nuevo más tarde.");
      });
  });
});
