/**
 * admin_quill.js
 * Inicializa Quill.js en el Django Admin para el campo de contenido.
 */
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('id_contenido');
    if (!textarea) return;

    // Crear contenedor para Quill
    const container = document.createElement('div');
    container.id = 'id_contenido_editor';
    // Aplicar estilos básicos para que coincida con el tema del admin
    container.style.backgroundColor = '#ffffff';
    container.style.color = '#333333';
    
    textarea.parentNode.insertBefore(container, textarea.nextSibling);
    textarea.style.display = 'none';

    // Barra de herramientas estilo Word
    const toolbarOptions = [
        [{ 'font': [] }],
        [{ 'size': ['small', false, 'large', 'huge'] }],
        ['bold', 'italic', 'underline', 'strike'],
        [{ 'color': [] }, { 'background': [] }],
        [{ 'script': 'sub'}, { 'script': 'super' }],
        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
        [{ 'indent': '-1'}, { 'indent': '+1' }],
        [{ 'align': [] }],
        ['clean']
    ];

    // Cargar estilos de Quill si no están cargados
    if (!document.getElementById('quill-css-admin')) {
        const link = document.createElement('link');
        link.id = 'quill-css-admin';
        link.rel = 'stylesheet';
        link.href = 'https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.snow.css';
        document.head.appendChild(link);
    }

    const quill = new Quill(container, {
        modules: {
            toolbar: toolbarOptions
        },
        theme: 'snow'
    });

    // Cargar valor original
    if (textarea.value) {
        quill.root.innerHTML = textarea.value;
    }

    // Sincronizar cambios al textarea
    quill.on('text-change', function() {
        textarea.value = quill.root.innerHTML === '<p><br></p>' ? '' : quill.root.innerHTML;
    });

    // Ajustes de altura del editor en el admin
    const editor = container.querySelector('.ql-editor');
    if (editor) {
        editor.style.minHeight = '300px';
        editor.style.maxHeight = '600px';
    }
});
