<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { goto } from '$app/navigation';

  export let mensaje = 'Cronograma creado correctamente';
  export let destino = '/inicio';
  export let delay = 2000; 

  let visible = true;

  onMount(() => {
    const t = setTimeout(() => {
      visible = false;
      setTimeout(() => goto(destino), 500);
    }, delay);
    return () => clearTimeout(t);
  });
</script>

{#if visible}
  <div class="toast" in:fly={{ y: -20, duration: 200 }} out:fade={{ duration: 300 }}>
    <div class="msg">
      ✅ {mensaje}
    </div>
  </div>
{/if}

<style>
.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: #22c55e;
  color: white;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,.2);
  font-size: 0.95rem;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 260px;
}
.msg {
  flex: 1;
}
</style>
