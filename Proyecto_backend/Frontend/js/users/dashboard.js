document.addEventListener('DOMContentLoaded', () => {
    // 1. Verificar Autenticación
    const userId = localStorage.getItem('id'); 
    const name = localStorage.getItem('name');
    
    if (!userId) {
        window.location.href = 'login.html';
        return;
    }
    
    //  nombre de usuario
    const userNameElement = document.getElementById('name');
    if(userNameElement) userNameElement.textContent = `Hola, ${name || 'Usuario'}`;

    // --- LÓGICA DE NAVEGACIÓN (SIDEBAR) ---
    const menuItems = document.querySelectorAll('.menu-item');
    const sections = document.querySelectorAll('.view-section');
    const pageTitle = document.getElementById('page-title');

    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            if (item.classList.contains('logout')) return; // Ignorar botón logout

            // Activar botón menú
            menuItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            // Mostrar sección correspondiente
            const targetId = item.getAttribute('data-target');
            sections.forEach(sec => sec.classList.add('hidden'));
            document.getElementById(targetId).classList.remove('hidden');

            // Actualizar título
            pageTitle.textContent = item.innerText;
        });
    });

});

document.addEventListener('DOMContentLoaded', () => {
    console.log("Dashboard JS cargado correctamente");

    // 1. Verificar Auth
    const userId = localStorage.getItem('id'); 
    if (!userId) {
        console.log("No hay usuario, redirigiendo...");
        window.location.href = 'login.html';
        return;
    }

    // 2. Lógica del Menú
    const menuItems = document.querySelectorAll('.menu-item');
    const sections = document.querySelectorAll('.view-section');

    console.log(`Encontrados ${menuItems.length} botones de menú y ${sections.length} secciones.`);

    menuItems.forEach(item => {
        item.addEventListener('click', (e) => {
            console.log("Click en botón:", item.innerText);
            
            if (item.classList.contains('logout')) return;

            // Quitar active de todos
            menuItems.forEach(i => i.classList.remove('active'));
            // Poner active al actual
            item.classList.add('active');

            // Ocultar todas las secciones
            sections.forEach(sec => {
                sec.classList.add('hidden');
                console.log("Ocultando sección:", sec.id);
            });

            // Mostrar la correcta
            const targetId = item.getAttribute('data-target');
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {
                targetSection.classList.remove('hidden');
                console.log("Mostrando sección:", targetId);
            } else {
                console.error("No se encontró la sección con ID:", targetId);
            }
        });
    });
    
    // Logout
    const btnLogout = document.getElementById('btn-logout');
    if(btnLogout) {
        btnLogout.addEventListener('click', () => {
            localStorage.clear();
            window.location.href = 'login.html';
        });
    }
});