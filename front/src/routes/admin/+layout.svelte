
<script>
    import '$lib/styles/admin-layout.css';
    import { user as userStore } from '$lib/login/authService';
</script>

 <div class="admin-layout">
    <header class="admin-header">
       <div class="logo">
            <a href="/admin">Panel de Administración</a>
        </div>
   </header>

    <div class="admin-main">
        <main class="admin-content-full">
            <slot></slot>
        </main>
    </div>
</div>
