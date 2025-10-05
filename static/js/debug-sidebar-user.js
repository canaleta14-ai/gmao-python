// Script de diagnóstico para el nombre de usuario en el sidebar
console.log('🔍 DIAGNÓSTICO DEL SIDEBAR - NOMBRE DE USUARIO');
console.log('='.repeat(50));

// 1. Verificar elemento existe
const userElement = document.getElementById('current-user');
console.log('1️⃣ Elemento #current-user:', userElement ? '✅ Existe' : '❌ No encontrado');

if (userElement) {
    // 2. Verificar contenido actual
    console.log('2️⃣ Contenido actual:', userElement.textContent);
    
    // 3. Verificar estilos computados
    const styles = window.getComputedStyle(userElement);
    console.log('3️⃣ Estilos aplicados:');
    console.log('   - Color:', styles.color);
    console.log('   - Background:', styles.backgroundColor);
    console.log('   - Font-weight:', styles.fontWeight);
    console.log('   - Visibility:', styles.visibility);
    console.log('   - Display:', styles.display);
    console.log('   - Opacity:', styles.opacity);
    
    // 4. Verificar clases CSS
    console.log('4️⃣ Clases CSS:', userElement.className);
    
    // 5. Verificar elemento padre
    const parent = userElement.parentElement;
    console.log('5️⃣ Elemento padre:', parent?.className);
    const parentStyles = window.getComputedStyle(parent);
    console.log('   - Color del padre:', parentStyles.color);
}

// 6. Verificar variable global currentUser
console.log('6️⃣ Variable currentUser:', typeof currentUser !== 'undefined' ? currentUser : '❌ No definida');

// 7. Verificar respuesta de API
console.log('7️⃣ Probando API /api/user/info...');
fetch('/api/user/info')
    .then(r => r.json())
    .then(data => {
        console.log('   ✅ API Response:', data);
        if (data.success && data.user) {
            console.log('   📝 Nombre del usuario:', data.user.nombre);
            console.log('   📝 Username:', data.user.username);
        }
    })
    .catch(err => console.error('   ❌ Error API:', err));

// 8. Forzar actualización manual
if (userElement) {
    console.log('8️⃣ Intentando forzar actualización...');
    setTimeout(() => {
        fetch('/api/user/info')
            .then(r => r.json())
            .then(data => {
                if (data.success && data.user) {
                    const nombre = data.user.nombre || data.user.username;
                    userElement.textContent = nombre;
                    userElement.style.color = '#ffffff';
                    userElement.style.fontWeight = '600';
                    console.log('   ✅ Actualizado manualmente a:', nombre);
                }
            });
    }, 1000);
}

console.log('='.repeat(50));
console.log('📋 Ejecuta este script en la consola del navegador');
console.log('   y comparte los resultados completos');
