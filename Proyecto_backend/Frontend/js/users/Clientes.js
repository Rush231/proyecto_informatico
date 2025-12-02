document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-cliente');
    const msg = document.getElementById('msg-cliente');
    const listaDiv = document.getElementById('lista-clientes');

    if (!form) return;

    // 1. Función para cargar clientes (Asumiendo que tienes esta ruta GET)
    function cargarClientes() {
        // Nota: Asegúrate de tener @app.route('/clientes', methods=['GET']) en tu Python
        fetch(apiURL + '/clientes') 
            .then(res => {
                if(!res.ok) throw new Error("No hay ruta GET /clientes");
                return res.json();
            })
            .then(data => {
                if (data.length === 0) {
                    listaDiv.innerHTML = '<p>No hay clientes registrados.</p>';
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
                console.log(err);
                listaDiv.innerHTML = '<p>Lista no disponible (Falta ruta GET en Backend).</p>';
            });
    }

    cargarClientes();

    // 2. Registrar Cliente
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        msg.textContent = "Registrando...";
        msg.className = "msg";

        const data = {
            name: document.getElementById('cli-nombre').value,
            email: document.getElementById('cli-email').value
        };

        try {
            const response = await fetch(apiURL + '/crear-cliente', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                msg.textContent = "Cliente registrado!";
                msg.className = "msg success";
                form.reset();
                cargarClientes();
            } else {
                msg.textContent = "Error al registrar";
                msg.className = "msg error";
            }
        } catch (error) {
            msg.textContent = "Error de conexión";
            msg.className = "msg error";
        }
    });
});