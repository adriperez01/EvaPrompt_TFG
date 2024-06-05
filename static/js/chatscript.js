document.addEventListener('DOMContentLoaded', function () {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const metricsContainer = document.getElementById('metrics-container');
    const errorMessageBox = document.getElementById('error-message');
    let chatMessages = [];

    window.sendChatMessage = function () {
        const userMessage = userInput.value.trim().replace(/\n/g, '<br>');
        const nombre = document.getElementById("nombre").value.trim();
        const datasetEvaluar = document.getElementById("datasetEvaluar").value.trim();
        const tecnicaUtilizada = document.getElementById("tecnicaUtilizada").value.trim();
        const limiteFilas = document.getElementById("limite-filas").value;
        // Validar que todos los campos estén completos
        if (!userMessage || !nombre || !datasetEvaluar || !tecnicaUtilizada) {
            errorMessageBox.textContent = 'Por favor, rellena todos los campos antes de enviar el mensaje.';
            errorMessageBox.style.display = 'block';
            return;
        }

        // Ocultar mensaje de error si todo está correcto
        errorMessageBox.style.display = 'none';

        chatBox.innerHTML += `<p class="user-message"><strong>Tú:</strong> ${userMessage.replace(/\n/g, '<br>')}</p>`;
        chatBox.scrollTop = chatBox.scrollHeight;

        setTimeout(() => {
            chatBox.innerHTML += `<p class="sistem-message"><strong>Evaluación en curso</strong></p>`;
            chatBox.innerHTML += `<p class="typing-message"><strong>Realizando pruebas<span class="typing-dots">...</span></strong></p>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        }, 1000);

        fetch('/v1/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                message: userMessage,
                nombre: nombre,
                datasetEvaluar: datasetEvaluar,
                tecnicaUtilizada: tecnicaUtilizada,
                limiteFilas:limiteFilas
            }),
        })
        .then(response => response.json())
        .then(data => {
            const typingMessage = document.querySelector('.typing-message');
            if (typingMessage) {
                typingMessage.remove();
            }

            if (data.prompt && Array.isArray(data.prompt)) {
                data.prompt.forEach((prompt, index) => {
                    setTimeout(() => {
                        chatBox.innerHTML += `<p class="user-message"><strong>Tú:</strong> ${prompt.replace(/\n/g, '<br>')}</p>`;
                        chatBox.innerHTML += `<p class="eva-message"><strong>Eva:</strong> ${data.message[index].replace(/\n/g, '<br>')}</p>`;
                        chatBox.scrollTop = chatBox.scrollHeight;
                    }, (index * 2) * 1000);
                });
            } else {
                console.error('Error: data.prompt is undefined or not an array');
            }
            console.log(data)
            document.getElementById('priority_accuracy').textContent = data.priority_accuracy.toFixed(2);
            document.getElementById('precision').textContent = data.precision.toFixed(2);
            document.getElementById('recall').textContent = data.recall.toFixed(2);
            document.getElementById('f1_score').textContent = data.f1_score.toFixed(2);
            
            setTimeout(() => {
                const sistemaMessage = document.querySelector('.sistem-message');
                if (sistemaMessage) {
                    sistemaMessage.innerHTML = `<strong>EVALUACION COMPLETADA</strong>`;
                }
            }, (data.prompt && data.prompt.length || 0) * 2 * 1000);
        })
        .catch(error => {
            console.error('Error al enviar o recibir mensajes:', error);
            chatBox.innerHTML += `<p class="error-message">Ha ocurrido un error. Por favor, inténtalo de nuevo más tarde.</p>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        });

        userInput.value = '';
    };

    // Manejar el envío del formulario con JavaScript
    document.getElementById('promptForm').addEventListener('submit', function(event) {
        event.preventDefault();
        sendChatMessage();
    });

    // Manejar el envío del formulario al presionar Enter en el campo de entrada
    userInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendChatMessage();
        }
    });

});
