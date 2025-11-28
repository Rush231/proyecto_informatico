document.addEventListener("DOMContentLoaded", () => {
    // Limpiar cualquier dato de sesión previo
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("id");
});


function userLogin() {
    // Obtener los valores ingresados en el formulario
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    // Elemento para mostrar mensajes al usuario
    const messageElement = document.getElementById("message");
    messageElement.classList.remove('error', 'success');

     // Elementos para mostrar una animación de carga sobre el botón del formulario
     const submitBtn = document.getElementById('login-btn');
     const spinner = document.getElementById('loading-spinner');

    // Validación de campos
    if (!username || !password) {
        messageElement.innerHTML = "Por favor, complete ambos campos.";
        messageElement.classList.add('error');
        return;
    }

    // Mostrar un mensaje de carga
    messageElement.innerHTML = "Iniciando sesión...";
    // Mostrar el spinner y desactivar el botón mientras se procesa la solicitud
    spinner.style.display = 'inline-block';
    submitBtn.disabled = true;

    // Configuración de la solicitud
    const credentials = btoa(`${username}:${password}`);
    const requestOptions = {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Basic ${credentials}`
        }
    };

    // Realizar la solicitud de inicio de sesión
    fetch(apiURL + '/login', requestOptions)
        .then(response => handleResponse(response))
        .then(response => {
            if (response.token) {
                // Almacenar los datos de sesión en localStorage
                localStorage.setItem("token", response.token);
                localStorage.setItem("username", response.username);
                localStorage.setItem("id", response.id);

                // Redirigir al usuario al dashboard
                window.location.href = "dashboard.html";
            } else {
                // Mensaje en caso de que no se obtenga un token
                messageElement.innerHTML = response.message || "Error al iniciar sesión.";
                messageElement.classList.add('error');
            }
        })
        .catch(error => {
            // Hubo algún error, ya sea en respueta de la API o error de conexión
            if (error.message === "Failed to fetch") {
                messageElement.innerHTML = "No se pudo conectar con el servidor. Verifique su conexión o intente más tarde.";
            } else {
                messageElement.innerHTML = error.message || "Error al iniciar sesión";
            }
            messageElement.classList.add('error');
            messageElement.classList.add('error');
        })
        .finally(() => {
            // Ocultar el spinner y activar el botón nuevamente
            spinner.style.display = 'none';
            submitBtn.disabled = false;
        });
}
