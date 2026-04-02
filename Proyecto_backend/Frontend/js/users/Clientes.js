document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-cliente');
    const msg = document.getElementById('msg-cliente');
    const listaDiv = document.getElementById('lista-clientes');

    if (!form) return;

 function cargarClientes() {
        // Obtenemos el ID del negocio del administrador logueado
        const negocioId = localStorage.getItem('negocio_id'); 

        // Enviamos el negocio_id como parámetro en la URL
        fetch(`${apiURL}/clientes?negocio_id=${negocioId}`) 
            .then(res => {
                if(!res.ok) throw new Error("Error al obtener clientes del negocio");
                return res.json();
            })
            .then(data => {
                if (data.length === 0) {
                    listaDiv.innerHTML = '<p>No hay clientes registrados en su negocio.</p>';
                    return;
                }
                let html = '<ul style="list-style:none; padding:0;">';
                data.forEach(c => {
                    html += `<li style="padding:10px; border-bottom:1px solid #eee;">
                                👤 <strong>${c.name}</strong> (${c.email})
                             </li>`;
                });
                html += '</ul>';
                listaDiv.innerHTML = html;
            })
            .catch(err => {
                console.error(err);
                listaDiv.innerHTML = '<p>Error: No se pudieron cargar los clientes.</p>';
            });
    }

    cargarClientes();

    // 2. Registrar Cliente
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        msg.textContent = "Registrando...";
        msg.className = "msg";

        // Incluimos el negocio_id en los datos que enviamos al servidor
        const data = {
            name: document.getElementById('cli-nombre').value,
            email: document.getElementById('cli-email').value,
            negocio_id: localStorage.getItem('negocio_id')|| 1 // <--- VITAL PARA SAAS
        };

        try {
            // Asegúrate de que la ruta coincida con tu api/routes/Cliente.py
            const response = await fetch(apiURL + '/clientes', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                msg.textContent = "¡Cliente registrado exitosamente!";
                msg.className = "msg success";
                form.reset();
                cargarClientes(); // Recargamos la lista filtrada
            } else {
                const errorInfo = await response.json();
                msg.textContent = errorInfo.error || "Error al registrar";
                msg.className = "msg error";
            }
        } catch (error) {
            msg.textContent = "Error de conexión con el servidor";
            msg.className = "msg error";
        }
    });
});