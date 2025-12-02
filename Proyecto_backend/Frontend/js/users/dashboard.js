document.addEventListener('DOMContentLoaded', () => {
    // 1. Verificar Autenticación (Simple)
    const userId = localStorage.getItem('user_id'); // Asegúrate de guardar esto en el Login
    const userName = localStorage.getItem('user_name');
    
    if (!userId) {
        window.location.href = 'login.html';
        return;
    }
    
    document.getElementById('user-name').textContent = `Hola, ${userName || 'Usuario'}`;

    // 2. Referencias al DOM
    const selectNegocio = document.getElementById('select-negocio');
    const selectServicio = document.getElementById('select-servicio');
    const selectProfesional = document.getElementById('select-profesional');
    const formTurno = document.getElementById('form-turno');
    const msgDiv = document.getElementById('mensaje-reserva');

    // 3. Cargar Negocios al inicio
    fetch('http://localhost:5000/negocios') // Ajusta el puerto si es necesario
        .then(res => res.json())
        .then(data => {
            data.forEach(negocio => {
                const option = document.createElement('option');
                option.value = negocio.id;
                option.textContent = negocio.name;
                selectNegocio.appendChild(option);
            });
        })
        .catch(err => console.error("Error cargando negocios:", err));

    // 4. Lógica de Cambio de Negocio (Carga en cascada)
    selectNegocio.addEventListener('change', (e) => {
        const negocioId = e.target.value;
        
        // Resetear selects
        selectServicio.innerHTML = '<option value="">-- Selecciona Servicio --</option>';
        selectProfesional.innerHTML = '<option value="">-- Selecciona Profesional --</option>';
        selectServicio.disabled = true;
        selectProfesional.disabled = true;

        if (!negocioId) return;

        // Cargar Servicios del Negocio
        fetch(`http://localhost:5000/servicios?negocio_id=${negocioId}`)
            .then(res => res.json())
            .then(servicios => {
                servicios.forEach(s => {
                    const opt = document.createElement('option');
                    opt.value = s.id;
                    opt.textContent = `${s.nombre} (${s.duracion} min)`;
                    selectServicio.appendChild(opt);
                });
                selectServicio.disabled = false;
            });

        // Cargar Profesionales del Negocio
        fetch(`http://localhost:5000/profesionales?negocio_id=${negocioId}`)
            .then(res => res.json())
            .then(profesionales => {
                profesionales.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.id;
                    opt.textContent = p.name; // Asegúrate que el back devuelva 'name'
                    selectProfesional.appendChild(opt);
                });
                selectProfesional.disabled = false;
            });
    });

    // 5. Manejar el envío del Turno
    formTurno.addEventListener('submit', async (e) => {
        e.preventDefault();
        msgDiv.textContent = "Procesando...";
        msgDiv.className = "msg";

        // Obtener datos
        const servicioId = selectServicio.value;
        const profesionalId = selectProfesional.value;
        const fechaInput = document.getElementById('input-fecha').value; // Viene como "2023-11-20T10:30"

        if (!fechaInput) {
            alert("Por favor selecciona una fecha");
            return;
        }

        // FORMATEAR FECHA: Eliminar la 'T' para que sea "YYYY-MM-DD HH:MM:SS"
        const fechaFormateada = fechaInput.replace('T', ' ') + ':00';

        const datosTurno = {
            cliente_id: userId,
            profesional_id: profesionalId,
            servicio_id: servicioId,
            fecha_hora: fechaFormateada
        };

        try {
            const response = await fetch('http://localhost:5000/crear-turno', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datosTurno)
            });

            const data = await response.json();

            if (response.ok) {
                msgDiv.textContent = "¡Turno reservado con éxito!";
                msgDiv.className = "msg success";
                formTurno.reset();
            } else {
                // Aquí mostramos el error que venía del backend (ej. "Horario ocupado")
                msgDiv.textContent = `Error: ${data.error || 'No se pudo reservar'}`;
                msgDiv.className = "msg error";
            }
        } catch (error) {
            msgDiv.textContent = "Error de conexión con el servidor";
            msgDiv.className = "msg error";
        }
    });

    // Logout
    document.getElementById('btn-logout').addEventListener('click', () => {
        localStorage.clear();
        window.location.href = 'login.html';
    });
});