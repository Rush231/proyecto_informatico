document.addEventListener('DOMContentLoaded', () => {
    const selectNegocio = document.getElementById('select-negocio');
    const selectServicio = document.getElementById('select-servicio');
    const selectProfesional = document.getElementById('select-profesional');
    const formTurno = document.getElementById('form-turno');
    const msgDiv = document.getElementById('mensaje-reserva');
    const userId = localStorage.getItem('id');

    // Solo ejecutar si existe el elemento en el HTML actual
    if (!selectNegocio) return; 

    // 1. Cargar Negocios
    fetch(apiURL + '/negocios')
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
        .catch(err => console.error("Error cargando negocios:", err));

    // 2. Cambio de Negocio (Cascada)
    selectNegocio.addEventListener('change', (e) => {
        const negocioId = e.target.value;
        selectServicio.innerHTML = '<option value="">-- Selecciona Servicio --</option>';
        selectProfesional.innerHTML = '<option value="">-- Selecciona Profesional --</option>';
        selectServicio.disabled = true;
        selectProfesional.disabled = true;

        if (!negocioId) return;

        // Fetch Servicios
        fetch(`${apiURL}/servicios?negocio_id=${negocioId}`)
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

        // Fetch Profesionales
        fetch(`${apiURL}/profesionales?negocio_id=${negocioId}`)
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

    // 3. Enviar Turno
    formTurno.addEventListener('submit', async (e) => {
        e.preventDefault();
        msgDiv.textContent = "Procesando...";
        msgDiv.className = "msg";

        const datosTurno = {
            cliente_id: userId,
            profesional_id: selectProfesional.value,
            servicio_id: selectServicio.value,
            fecha_hora: document.getElementById('input-fecha').value.replace('T', ' ') + ':00'
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
            } else {
                msgDiv.textContent = `Error: ${data.error || 'No se pudo reservar'}`;
                msgDiv.className = "msg error";
            }
        } catch (error) {
            msgDiv.textContent = "Error de conexión";
            msgDiv.className = "msg error";
        }
    });
});