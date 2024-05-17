document.addEventListener('DOMContentLoaded', function () {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const accuracyContainer = document.getElementById('accuracy-container');
    let chatMessages = []; // Variable para almacenar todos los mensajes
    window.sendChatMessage = function () {
        const userMessage = userInput.value.trim();
        const nombre = document.getElementById("nombre").value;
        const datasetEvaluar = document.getElementById("datasetEvaluar").value;
        const tecnicaUtilizada = document.getElementById("tecnicaUtilizada").value;
        if (userMessage !== '') {
        // Imprimir el mensaje del usuario en 'Tú' en el chat
        chatBox.innerHTML += `<p class="user-message"><strong>Tú:</strong> ${userMessage}</p>`;
        chatBox.scrollTop = chatBox.scrollHeight; // Desplazar hacia abajo para mostrar el último mensaje

        setTimeout(() => {
            chatBox.innerHTML += `<p class="sistem-message"><strong>Evaluación en curso</strong></p>`;
            chatBox.innerHTML += `<p class="typing-message"><strong>Realizando pruebas<span class="typing-dots">...</span></strong></p>`;
            chatBox.scrollTop = chatBox.scrollHeight; // Desplazar hacia abajo para mostrar el último mensaje
        }, 1000); // Esperar 1000 milisegundos (1 segundo)
            // Llamar a la función basic_prompt con el mensaje del usuario y otros datos
            fetch('/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: userMessage,
                    nombre: nombre,
                    datasetEvaluar: datasetEvaluar,
                    tecnicaUtilizada: tecnicaUtilizada
                }),
            })
            .then(response => response.json())
            .then(data => {
                // Eliminar el mensaje de "escribiendo..."
                const typingMessage = document.querySelector('.typing-message');
                if (typingMessage) {
                    typingMessage.remove();
                }
    
                // Imprimir la respuesta de basic_prompt en 'Eva' en el chat
                console.log(data);
                // Utilizar setTimeout para mostrar los mensajes uno por uno con un retraso de 1 segundo entre cada par de mensajes
                data.prompt.forEach((prompt, index) => {
                    setTimeout(() => {
                        chatBox.innerHTML += `<p class="user-message"><strong>Tú:</strong> ${prompt}</p>`;
                        chatBox.innerHTML += `<p class="eva-message"><strong>Eva:</strong> ${data.message[index]}</p>`;
                        chatBox.scrollTop = chatBox.scrollHeight; // Desplazar hacia abajo para mostrar el último mensaje
                    }, (index * 2) * 1000); // Se multiplica por 2 para que el retraso se aplique después de cada par de mensajes
                });
                // Actualizar contenedor de precisión de prioridad
                accuracyContainer.innerHTML = `<div class="accuracy-container"><p>Accuracy: ${data.priority_accuracy}</p></div>`;
                setTimeout(() => {
                    const sistemaMessage = document.querySelector('.sistem-message');
                    if (sistemaMessage) {
                        sistemaMessage.innerHTML = `<strong>EVALUACION COMPLETADA</strong>`;
                    }
                }, (data.prompt.length * 2 + 1) * 1000); // Se suma 1 segundo al total de tiempo antes de cambiar el mensaje
            })
            .catch(error => {
                // Manejar errores de red
                console.error('Error al enviar o recibir mensajes:', error);
                chatBox.innerHTML += `<p class="error-message">Ha ocurrido un error. Por favor, inténtalo de nuevo más tarde.</p>`;
                chatBox.scrollTop = chatBox.scrollHeight; // Desplazar hacia abajo para mostrar el último mensaje
            });
    
            userInput.value = '';
        }
    };
    

// Manejar el envío del formulario con JavaScript
document.getElementById('promptForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Evitar el comportamiento predeterminado del formulario
    sendChatMessage(); // Llamar a la función sendChatMessage para enviar el mensaje
});

// Manejar el envío del formulario al presionar Enter en el campo de entrada
userInput.addEventListener('keypress', function(event) {
    if (event.key === 13) {
        event.preventDefault(); // Evitar el comportamiento predeterminado de la tecla Enter
        sendChatMessage(); // Llamar a la función sendChatMessage para enviar el mensaje
    }
});

});

