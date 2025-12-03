document.addEventListener('DOMContentLoaded', () => {
    const formProfesional = document.getElementById('form-crear-profesional');
    const selectProfNegocio = document.getElementById('prof-negocio');
    const msgProf = document.getElementById('msg-profesional');
    const listaProfDiv = document.getElementById('lista-profesionales-existentes');

    if (!formProfesional) return;

    // --- 1. FUNCIÓN PARA LISTAR (Ahora acepta un ID opcional) ---
    function cargarProfesionales(negocioId = null) {
        listaProfDiv.innerHTML = '<p>Cargando...</p>';
        
        // Si hay ID, usamos el filtro. Si no, pedimos todos.
        let url = apiURL + '/profesionales';
        if (negocioId) {
            url += `?negocio_id=${negocioId}`;
        }

        fetch(url)
            .then(res => res.json())
            .then(data => {
                if (!data || data.length === 0) {
                    listaProfDiv.innerHTML = '<p>No hay profesionales encontrados.</p>';
                    return;
                }
                
                let html = '<ul style="list-style:none; padding:0;">';
                data.forEach(prof => {
                    html += `
                        <li style="padding:10px; border-bottom:1px solid #eee; display:flex; justify-content:space-between;">
                            <span>👨‍⚕️ <strong>${prof.name}</strong> (${prof.especialidad || 'General'})</span>
                            <button class="btn-borrar" onclick="borrarProf(${prof.id})">❌</button>
                        </li>`;
                });
                html += '</ul>';
                listaProfDiv.innerHTML = html;
            });
    }

    // --- 2. CARGAR NEGOCIOS Y EVENTO DE CAMBIO ---
    fetch(apiURL + '/negocios')
        .then(res => res.json())
        .then(data => {
            selectProfNegocio.innerHTML = '<option value="">-- Ver Todos --</option>';
            data.forEach(n => {
                const opt = document.createElement('option');
                opt.value = n.id;
                opt.textContent = n.name;
                selectProfNegocio.appendChild(opt);
            });
        });

    // CUANDO CAMBIAS EL NEGOCIO -> SE FILTRA LA LISTA DE ABAJO
    selectProfNegocio.addEventListener('change', () => {
        const id = selectProfNegocio.value;
        cargarProfesionales(id); // Recarga la lista filtrada
    });

    // --- 3. CREAR PROFESIONAL ---
    formProfesional.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Validación simple
        if(!selectProfNegocio.value) {
            alert("Por favor selecciona un negocio");
            return;
        }

        const nuevoProf = {
            name: document.getElementById('prof-nombre').value,
            especialidad: document.getElementById('prof-especialidad').value,
            negocio_id: selectProfNegocio.value
        };

        const response = await fetch(apiURL + '/crear-profesional', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(nuevoProf)
        });

        if (response.ok) {
            msgProf.textContent = "¡Creado!";
            msgProf.className = "msg success";
            formProfesional.reset();
            // Recargar la lista del negocio actual
            cargarProfesionales(nuevoProf.negocio_id);
            // Restaurar el select para que siga en el mismo negocio
            selectProfNegocio.value = nuevoProf.negocio_id;
        } else {
            msgProf.textContent = "Error al crear";
            msgProf.className = "msg error";
        }
    });

    
    cargarProfesionales();
    
    // Función global para el botón borrar (para que funcione el onclick del HTML string)
    window.borrarProf = (id) => {
        if(!confirm('¿Quieres eliminar a esta persona?')) return;
        fetch(`${apiURL}/profesional/borrar/${id}`, { method: 'DELETE' })
            .then(res => {
                if(res.ok) { 
                    // Recargar la lista según lo que esté seleccionado en el combo
                    cargarProfesionales(selectProfNegocio.value); 
                }
            });
    };
});