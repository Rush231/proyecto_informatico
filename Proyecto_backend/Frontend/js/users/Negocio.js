document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-negocio');
    const msg = document.getElementById('msg-negocio');
    const listaDiv = document.getElementById('lista-negocios');

    if (!form) return;

    // 1. Función para cargar lista
    function cargarNegocios() {
        fetch(apiURL + '/negocios')
            .then(res => res.json())
            .then(data => {
                if (data.length === 0) {
                    listaDiv.innerHTML = '<p>No hay negocios registrados.</p>';
                    return;
                }
                let html = '<ul style="list-style:none; padding:0;">';
                data.forEach(n => {
                    html += `<li style="padding:10px; border-bottom:1px solid #eee;">
                                <strong>${n.name}</strong> (${n.tipo || 'Sin tipo'})
                             </li>`;
                });
                html += '</ul>';
                listaDiv.innerHTML = html;
            })
            .catch(err => listaDiv.innerHTML = '<p>Error al cargar.</p>');
    }

    // Cargar al inicio
    cargarNegocios();

    // 2. Guardar Negocio
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        msg.textContent = "Guardando...";
        msg.className = "msg";

        const data = {
            name: document.getElementById('negocio-nombre').value,
            tipo: document.getElementById('negocio-tipo').value
        };

        try {
            const response = await fetch(apiURL + '/negocio/crear-negocio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                msg.textContent = "¡Negocio creado!";
                msg.className = "msg success";
                form.reset();
                cargarNegocios(); // Actualizar lista
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