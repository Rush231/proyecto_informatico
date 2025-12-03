document.addEventListener('DOMContentLoaded', () => {
    const selectNegocio = document.getElementById('select-negocio');
    const selectServicio = document.getElementById('select-servicio');
    const selectProfesional = document.getElementById('select-profesional');
    const formTurno = document.getElementById('form-turno');
    const msgDiv = document.getElementById('mensaje-reserva');
    const userId = localStorage.getItem('id');
    const selectCliente = document.getElementById('select-cliente-turno');

    // 1. IMPORTANTE: Verificar que los elementos existan antes de seguir
    // Si selectNegocio no existe, detenemos el script para evitar errores.
    if (!selectNegocio || !selectServicio || !selectProfesional || !formTurno) {
        // Opcional: console.log("Turnos.js: No estamos en la vista de turnos o faltan elementos.");
        return; 
    }

    // 2. Cargar Negocios
    fetch(apiURL + '/negocios') // apiURL viene de common.js
        .then(res => res.json())
        .then(data => {
            selectNegocio.innerHTML = '<option value="">-- Selecciona Negocio --</option>';
            data.forEach(negocio => {
                const option = document.createElement('option');
                option.value = negocio.id;
                option.textContent = negocio.name;
                selectNegocio.appendChild(option);
            });
        })
        .catch(err => console.error("Error cargando negocios:", err)); // Asegúrate que diga "negocios"

    // 3. Cambio de Negocio (Cascada)
    selectNegocio.addEventListener('change', (e) => {
        const negocioId = e.target.value;
        selectServicio.innerHTML = '<option value="">-- Selecciona Servicio --</option>';
        selectProfesional.innerHTML = '<option value="">-- Selecciona Profesional --</option>';
        
        // Deshabilitar hasta que se seleccione algo
        selectServicio.disabled = true;
        selectProfesional.disabled = true;

        if (!negocioId) return;

        // Fetch Servicios
        fetch(`${apiURL}/servicios/${negocioId}`)
            .then(res => res.json())
            .then(servicios => {
                servicios.forEach(s => {
                    const opt = document.createElement('option');
                    opt.value = s.id;
                    opt.textContent = `${s.name} (${s.duracion} min)`;
                    selectServicio.appendChild(opt);
                });
                selectServicio.disabled = false;
            });

        // Fetch Profesionales (CORREGIDO: quitada la doble barra //)
        fetch(`${apiURL}/profesionales/${negocioId}`) 
            .then(res => res.json())
            .then(profesionales => {
                profesionales.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.id;
                    opt.textContent = p.name;
                    selectProfesional.appendChild(opt);
                });
                selectProfesional.disabled = false;
            });
    });

    // 4. Enviar Turno
    formTurno.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Verificar nuevamente valores nulos por seguridad
        if (!selectProfesional.value || !selectServicio.value) {
            msgDiv.textContent = "Por favor selecciona todos los campos.";
            msgDiv.className = "msg error";
            return;
        }

        msgDiv.textContent = "Procesando...";
        msgDiv.className = "msg";

        const inputFecha = document.getElementById('input-fecha');
        if (!inputFecha) return;

        const datosTurno = {
            cliente_id: selectCliente,
            profesional_id: selectProfesional.value,
            servicio_id: selectServicio.value,
            fecha_hora: inputFecha.value.replace('T', ' ') + ':00'
        };

        try {
            const response = await fetch(`${apiURL}/crear-turno`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datosTurno)
            });
            const data = await response.json();

            if (response.ok) {
                msgDiv.textContent = "¡Turno reservado con éxito!";
                msgDiv.className = "msg success";
                formTurno.reset();
                // Resetear selects dependientes
                selectServicio.innerHTML = '<option value="">-- Primero Negocio --</option>';
                selectProfesional.innerHTML = '<option value="">-- Primero Negocio --</option>';
                selectServicio.disabled = true;
                selectProfesional.disabled = true;
            } else {
                msgDiv.textContent = `Error: ${data.error || 'No se pudo reservar'}`;
                msgDiv.className = "msg error";
            }
        } catch (error) {
            msgDiv.textContent = "Error de conexión";
            msgDiv.className = "msg error";
            console.error(error);
        }
    });
});

