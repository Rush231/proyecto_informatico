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

    // PRUEBA DE FUEGO: Imprimir en consola para ver si el JS actual se está ejecutando
    console.log("DEBUG FRONTEND - El token a enviar es:", token); 

    fetch(`${apiURL}/clientes?negocio_id=${negocioid}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`, // <-- El token debe viajar aquí
            'Content-Type': 'application/json'
        }
    })
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

    // Cargar la lista al entrar
    cargarClientes();

    // 2. Registrar Cliente
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    msg.textContent = "Registrando...";
    msg.className = "msg";

    const token = localStorage.getItem('token'); // Recuperar el token guardado

    const data = {
        name: document.getElementById('cli-nombre').value,
        email: document.getElementById('cli-email').value,
        negocio_id: localStorage.getItem('negocio_id') 
    };

    try {
        // Asegúrate de que la ruta coincida. En tu Cliente.py la ruta es '/crear'
        const response = await fetch(apiURL + '/crear', { 
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`  // <-- ENVIAMOS EL TOKEN AQUÍ
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            msg.textContent = "¡Cliente registrado exitosamente!";
            msg.className = "msg success";
            form.reset();
            cargarClientes(); 
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