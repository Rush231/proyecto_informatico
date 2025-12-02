document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-disponibilidad');
    const selectProf = document.getElementById('disp-profesional');
    const msg = document.getElementById('msg-disponibilidad');

    if (!form) return;

    // Función auxiliar para cargar profesionales de TODOS los negocios
    // (O podrías filtrar por negocio si tuvieras un select de negocio aquí también)
    function cargarProfesionales() {
        // Asumiendo que tienes una ruta para traer todos o filtras por el primer negocio que encuentres
        // Por simplicidad, aquí intentamos traer profesionales de un negocio ID=1 o adaptamos la API
        // Si tu API requiere obligatoriamente negocio_id, deberías agregar un select de negocio antes.
        
        // OPCIÓN A: Traer todos los negocios y luego todos sus profesionales (Cascada interna)
        fetch(apiURL + '/negocios')
            .then(res => res.json())
            .then(negocios => {
                selectProf.innerHTML = '<option value="">-- Selecciona Profesional --</option>';
                negocios.forEach(negocio => {
                    fetch(`${apiURL}/profesionales?negocio_id=${negocio.id}`)
                        .then(r => r.json())
                        .then(profs => {
                            profs.forEach(p => {
                                const opt = document.createElement('option');
                                opt.value = p.id;
                                opt.textContent = `${p.name} (${negocio.name})`;
                                selectProf.appendChild(opt);
                            });
                        });
                });
            });
    }

    cargarProfesionales();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        msg.textContent = "Guardando...";
        msg.className = "msg";

        const data = {
            profesional_id: selectProf.value,
            dia_semana: document.getElementById('disp-dia').value,
            hora_inicio: document.getElementById('disp-inicio').value, // Formato "HH:MM"
            hora_fin: document.getElementById('disp-fin').value
        };

        try {
            const response = await fetch(apiURL + '/crear_disponibilidad', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                msg.textContent = "Horario asignado correctamente";
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