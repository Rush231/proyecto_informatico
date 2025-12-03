document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-servicio');
    const selectNegocio = document.getElementById('serv-negocio');
    const msg = document.getElementById('msg-servicio');
    const listaDiv = document.getElementById('lista-servicios');

    if (!form) return;

    // 1. Cargar negocios en el select
    fetch(apiURL + '/negocios')
        .then(res => res.json())
        .then(data => {
            selectNegocio.innerHTML = '<option value="">-- Selecciona Negocio --</option>';
            data.forEach(n => {
                const opt = document.createElement('option');
                opt.value = n.id;
                opt.textContent = n.name;
                selectNegocio.appendChild(opt);
            });
        });

    // 2. Cargar servicios cuando cambia el negocio
    selectNegocio.addEventListener('change', () => {
        const id = selectNegocio.value;
        if(!id) return;
        
        listaDiv.innerHTML = 'Cargando...';
            fetch(`${apiURL}/servicios/${id}`)
            .then(res => res.json())
            .then(data => {
                if(data.length === 0) {
                    listaDiv.innerHTML = '<p>No hay servicios en este negocio.</p>';
                    return;
                }
                let html = '<ul style="list-style:none; padding:0;">';
                data.forEach(s => {
                    html += `<li style="padding:10px; border-bottom:1px solid #eee;">
                                 <strong>${s.name}</strong> -  ${s.duracion} min
                             </li>`;
                });
                html += '</ul>';
                listaDiv.innerHTML = html;
            });
    });

    // 3. Crear Servicio
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        msg.textContent = "Guardando...";
        msg.className = "msg";

        const data = {
            name: document.getElementById('serv-nombre').value,
            duracion: document.getElementById('serv-duracion').value,
            negocio_id: selectNegocio.value
        };

        try {
            const response = await fetch(apiURL + '/crear-servicio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                msg.textContent = "Servicio creado!";
                msg.className = "msg success";
                form.reset();
                // Disparar evento change para recargar la lista
                selectNegocio.dispatchEvent(new Event('change'));
            } else {
                msg.textContent = "Error al crear";
                msg.className = "msg error";
            }
        } catch (error) {
            msg.textContent = "Error de conexión";
            msg.className = "msg error";
        }
    });
});