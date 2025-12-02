            document.addEventListener('DOMContentLoaded', () => {
    const formProfesional = document.getElementById('form-crear-profesional');
    const selectProfNegocio = document.getElementById('prof-negocio');
    const msgProf = document.getElementById('msg-profesional');

    // Si no estamos en una página con este formulario, no hacemos nada
    if (!formProfesional) return;

    // 1. Cargar Negocios en el select de Profesionales
    fetch(apiURL + '/negocios')
        .then(res => res.json())
        .then(data => {
            selectProfNegocio.innerHTML = '<option value="">-- Selecciona Negocio --</option>';
            data.forEach(negocio => {
                const opt = document.createElement('option');
                opt.value = negocio.id;
                opt.textContent = negocio.name;
                selectProfNegocio.appendChild(opt);
            });
        });

    // 2. Crear Profesional
    formProfesional.addEventListener('submit', async (e) => {
        e.preventDefault();
        msgProf.textContent = "Guardando...";
        msgProf.className = "msg";

        const nuevoProf = {
            name: document.getElementById('prof-nombre').value,
            especialidad: document.getElementById('prof-especialidad').value,
            negocio_id: selectProfNegocio.value
        };

        try {
            const response = await fetch(apiURL + '/crear-profesional', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(nuevoProf)
            });

            if (response.ok) {
                msgProf.textContent = "Profesional creado correctamente";
                msgProf.className = "msg success";
                formProfesional.reset();
            } else {
                const data = await response.json();
                msgProf.textContent = data.error || "Error al crear";
                msgProf.className = "msg error";
            }
        } catch (error) {
            msgProf.textContent = "Error de conexión";
            msgProf.className = "msg error";
        }
    });
});