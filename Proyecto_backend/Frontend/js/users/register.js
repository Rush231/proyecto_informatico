function userRegister(){
    // Obtener los valores ingresados en el formulario
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Elemento para mostrar mensajes al usuario
    const messageElement = document.getElementById("message");
    messageElement.classList.remove('error', 'success');

    // Elementos para mostrar una animación de carga sobre el botón del formulario
    const submitBtn = document.getElementById('register-btn');
    const spinner = document.getElementById('loading-spinner');

    // Validación de campos
    if (!username || !password) {
        messageElement.innerHTML = "Por favor, complete ambos campos.";
        messageElement.classList.add('error');
        return;
    }

    // Mostrar un mensaje de carga
    messageElement.innerHTML = "Registrando su cuenta...";
    // Mostrar el spinner y desactivar el botón mientras se procesa la solicitud
    spinner.style.display = 'inline-block';
    submitBtn.disabled = true;

    // Configuración de la solicitud
    const requestOptions = {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
    };

    // Realizar la solicitud de creación de usuario
    fetch(apiURL + '/registro', requestOptions)
        .then(response => handleResponse(response))
        .then(response => {
            // El usuario se creó correctamente, si es necesario se usa el 
            // objeto response para ejecutar más acciones
            console.log(response)
            messageElement.innerHTML = "Usuario creado correctamente";
            messageElement.classList.add('success');            
        })
        .catch(error => {
            // Hubo algún error, ya sea en respueta de la API o error de conexión
            if (error.message === "Failed to fetch") {
                messageElement.innerHTML = "No se pudo conectar con el servidor. Verifique su conexión o intente más tarde.";
            } else {
                messageElement.innerHTML = error.message || "Error al crear el usuario";
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