document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-disponibilidad');
    const selectProf = document.getElementById('disp-profesional');
    const msg = document.getElementById('msg-disponibilidad');

    // 1. SEGURIDAD: Recuperar token
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    if (!form) return;

    // 2. CARGAR PROFESIONALES (Solo los míos, usando el Token)
    function cargarProfesionales() {
        // Ya no buscamos /negocios. Vamos directo a /profesionales con nuestra "llave"
        fetch(`${apiURL}/profesionales`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`, // <--- CLAVE
                'Content-Type': 'application/json'
            }
        })
        .then(res => {
            if (res.status === 401 || res.status === 403) {
                window.location.href = 'login.html';
                throw new Error("Sesión expirada");
            }
            return res.json();
        })
        .then(profs => {
            selectProf.innerHTML = '<option value="">-- Selecciona Profesional --</option>';
            
            // Validamos que sea un array antes de usar forEach
            if (Array.isArray(profs) && profs.length > 0) {
                profs.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.id;
                    opt.textContent = p.name; // Ya no hace falta mostrar el negocio, es obvio
                    selectProf.appendChild(opt);
                });
            } else {
                selectProf.innerHTML = '<option value="">No hay profesionales registrados</option>';
            }
        })
        .catch(err => console.error("Error cargando profesionales:", err));
    }

    cargarProfesionales();

    // 3. GUARDAR DISPONIBILIDAD (Con Token)
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        msg.textContent = "Guardando...";
        msg.className = "msg";

        const data = {
            profesional_id: selectProf.value,
            dia_semana: document.getElementById('disp-dia').value,
            hora_inicio: document.getElementById('disp-inicio').value + ":00", // Asegurar formato HH:MM:SS
            hora_fin: document.getElementById('disp-fin').value + ":00"
        };

        try {
            const response = await fetch(`${apiURL}/disponibilidad`, { // Asegúrate que la ruta en backend sea esta
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` // <--- CLAVE AQUÍ TAMBIÉN
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {msg.textContent = "Horario asignado correctamente";
                msg.className = "msg success";
                form.reset();
            } else {
                const info = await response.json();
                msg.textContent = info.error || "Error al asignar";
                msg.className = "msg error";
            }
        } catch (error) {
            msg.textContent = "Error de conexión";
            msg.className = "msg error";
        }
    });
});