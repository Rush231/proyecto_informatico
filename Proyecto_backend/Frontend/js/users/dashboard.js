document.addEventListener('DOMContentLoaded', () => {
    // 1. Verificar Autenticación y ROL
    const userId = localStorage.getItem('id'); 
    const name = localStorage.getItem('name');
    const rol = localStorage.getItem('rol'); // <--- OBTENEMOS EL ROL GUARDADO
    
    // Si no hay usuario, mandar al login
    if (!userId) {
        window.location.href = 'login.html';
        return;
    }
    
    // Mostrar nombre
    const userNameElement = document.getElementById('name');
    if(userNameElement) userNameElement.textContent = `Hola, ${name || 'Usuario'}`;

    // --- 2. LÓGICA DE SEGURIDAD (OCULTAR COSAS) ---
    // Si el rol NO es exactamente 'admin', borramos todo lo que diga 'admin-only'
    if (rol !== 'admin') {
        console.log("Acceso como EMPLEADO o ROL DESCONOCIDO. Ocultando funciones de admin.");
        
        // Buscamos todos los elementos con la clase "admin-only"
        const elementosProhibidos = document.querySelectorAll('.admin-only');
        
        elementosProhibidos.forEach(elemento => {
            elemento.remove(); // Los eliminamos del HTML
        });
    } else {
        console.log("Acceso como ADMIN. Se muestra todo.");
    }

    // --- 3. LÓGICA DE NAVEGACIÓN (SIDEBAR) ---
    const menuItems = document.querySelectorAll('.menu-item');
    const sections = document.querySelectorAll('.view-section');

    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            if (item.classList.contains('logout')) return; 

            // Activar botón menú
            menuItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            // Mostrar sección correspondiente
            const targetId = item.getAttribute('data-target');
            
            // Ocultar todas las secciones primero
            sections.forEach(sec => sec.classList.add('hidden'));
            
            // Mostrar la seleccionada si existe
            const targetSection = document.getElementById(targetId);
            if(targetSection) {
                targetSection.classList.remove('hidden');
            }
        });
    });
    
    // Botón Logout
    const btnLogout = document.getElementById('btn-logout');
    if(btnLogout) {
        btnLogout.addEventListener('click', () => {
            localStorage.clear();
            window.location.href = 'login.html';
        });
    }
});