document.addEventListener('DOMContentLoaded', () => {
   const form = document.getElementById('form-cliente');
    const msg = document.getElementById('msg-cliente');
    const listaDiv = document.getElementById('lista-clientes');

    // 1. RECUPERAR EL TOKEN (La llave maestra)
    const token = localStorage.getItem('token');

    // Si no hay token, lo mandamos al login (Seguridad Frontend)
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    if (!form) return;

    function cargarClientes() {
        // CAMBIO: Ya no enviamos "?negocio_id=..." en la URL.
        // Ahora enviamos el Token en los Headers.
        fetch(`${apiURL}/clientes`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // <--- ESTO ES LO QUE FALTABA
            }
        }) 
        .then(res => {
            if (res.status === 401 || res.status === 403) {
                alert("Su sesión ha expirado. Por favor ingrese nuevamente.");
                window.location.href = 'login.html';
                throw new Error("Token inválido");
            }
            if(!res.ok) throw new Error("Error al obtener clientes");
            return res.json();
        })
        .then(data => {
            if (data.length === 0) {
                listaDiv.innerHTML = '<p>No hay clientes registrados en su negocio.</p>';
                return;
            }
            let html = '<ul style="list-style:none; padding:0;">';
            data.forEach(c => {
                // Agregamos botón de eliminar para probar que funciona todo
                html += `
                    <li style="padding:10px; border-bottom:1px solid #eee; display:flex; justify-content:space-between;">
                        <span>👤 <strong>${c.name}</strong> (${c.email})</span>
                        <button onclick="eliminarCliente(${c.id})" style="color:red;">Eliminar</button>
                    </li>`;
            });
            html += '</ul>';
            listaDiv.innerHTML = html;
        })
        .catch(err => {
            console.error(err);
            listaDiv.innerHTML = '<p>Error al cargar la lista.</p>';
        });
    }

    // Cargar la lista al entrar
    cargarClientes();

    // 2. Registrar Cliente
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        msg.textContent = "Registrando...";
        msg.className = "msg";

        // CAMBIO: Ya no enviamos negocio_id manual. El backend lo pone solo.
        const data = {
            name: document.getElementById('cli-nombre').value,
            email: document.getElementById('cli-email').value
        };

        try {
            const response = await fetch(`${apiURL}/clientes`, { // Asegúrate que la ruta sea /clientes (plural)
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` // <--- TOKEN OBLIGATORIO AQUÍ TAMBIÉN
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                msg.textContent = "¡Cliente registrado exitosamente!";
                msg.className = "msg success";
                form.reset();
                cargarClientes(); // Recargamos la lista
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

    // Función global para eliminar (necesaria para el onclick del HTML generado)
    window.eliminarCliente = async (id) => {
        if(!confirm("¿Seguro que deseas eliminar este cliente?")) return;

        try {
            const res = await fetch(`${apiURL}/eliminar/${id}`, { // O la ruta que definiste para delete
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}` // <--- TOKEN PARA BORRAR
                }
            });

            if(res.ok) {
                alert("Cliente eliminado");
                cargarClientes();
            } else {
                const err = await res.json();
                alert("Error: " + (err.error || "No se pudo eliminar"));
            }
        } catch (e) {
            alert("Error de conexión");
        }
    };
});