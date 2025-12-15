<script>
  import { onMount, onDestroy } from "svelte";

  export let options = []; // [{ value, label }]
  export let value = [];
  export let placeholder = "Seleccionar";
  export let disabled = false;

  let open = false;
  let container;

  function toggleOpen() {
    if (disabled) return;
    open = !open;
  }

  function outside(e) {
    if (!container) return;
    if (!container.contains(e.target)) {
      open = false;
    }
  }

  function toggleValue(val) {
    if (disabled) return;
    const exists = (value || []).some((v) => String(v) === String(val));
    value = exists ? value.filter((v) => String(v) !== String(val)) : [...(value || []), val];
  }

  function isSelected(val) {
    return (value || []).some((v) => String(v) === String(val));
  }

  onMount(() => {
    document.addEventListener("click", outside);
  });

  onDestroy(() => {
    document.removeEventListener("click", outside);
  });
</script>

<div class="multiselect" bind:this={container}>
  <button class="multiselect-trigger" type="button" on:click={toggleOpen} disabled={disabled}>
    <div class="pill-container">
      {#if (value || []).length === 0}
        <span class="placeholder">{placeholder}</span>
      {:else}
        {#each value as val}
          {#if otp = options.find((o) => String(o.value) === String(val))}
            <span class="pill">
              {opt.label}
              <button type="button" class="pill-close" on:click={(e) => { e.stopPropagation(); toggleValue(val); }}>×</button>
            </span>
          {/if}
        {/each}
      {/if}
    </div>
    <span class="chevron">▼</span>
  </button>

  {#if open}
    <div class="multiselect-dropdown" on:click|stopPropagation>
      <div class="dropdown-actions">
        <button type="button" class="clear-btn" on:click={() => (value = [])}>Limpiar</button>
      </div>
      {#each options as opt}
        <label class="option">
          <input type="checkbox" checked={isSelected(opt.value)} on:change={() => toggleValue(opt.value)} />
          <span class="option-label">{opt.label}</span>
        </label>
      {/each}
      {#if !options || options.length === 0}
        <div class="no-options">Sin opciones</div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .multiselect { position: relative; width: 100%; }
  .multiselect-trigger {
    border: 1px solid #d6dce7;
    border-radius: 10px;
    background: #f9fafb;
    cursor: pointer;
    padding: 10px 12px;
    display: flex;
    align-items: flex-start;
    gap: 6px;
    width: 100%;
    min-height: 44px;
  }
  .multiselect-trigger:disabled { cursor: not-allowed; opacity: 0.6; }
  .multiselect-dropdown {
    position: absolute;
    z-index: 30;
    background: #fff;
    border: 1px solid #d6dce7;
    border-radius: 10px;
    max-height: 220px;
    overflow-y: auto;
    width: 100%;
    margin-top: 4px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
  }
  .dropdown-actions { display: flex; justify-content: flex-end; padding: 8px 10px; border-bottom: 1px solid #e5e7eb; }
  .clear-btn { background: transparent; border: none; color: #2f6fed; cursor: pointer; font-size: 13px; font-weight: 700; }
  .clear-btn:hover { text-decoration: underline; }
  .option { display: flex; align-items: center; gap: 8px; padding: 9px 12px; }
  .option:hover { background: #f3f6fb; }
  .option input { accent-color: #2f6fed; }
  .option-label { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .pill-container { display: flex; flex-wrap: wrap; gap: 6px; min-height: 24px; max-height: 72px; overflow-y: auto; align-items: flex-start; padding-right: 6px; width: 100%; }
  .pill { background: #f2f5fb; border: 1px solid #d6dce7; color: #0f172a; border-radius: 999px; padding: 4px 8px; display: inline-flex; align-items: center; gap: 6px; }
  .pill-close { border: none; background: transparent; cursor: pointer; font-weight: 700; color: #475569; }
  .chevron { font-size: 12px; color: #6b7280; margin-left: auto; }
  .placeholder { color: #6b7280; font-size: 14px; }
  .no-options { padding: 10px 12px; color: #6b7280; font-size: 13px; }
</style>
