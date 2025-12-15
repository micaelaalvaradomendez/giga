<nav class="navbar">
  <div class="navbar-container">
    <a href="/inicio" class="navbar-left">
      <div class="logo-title-wrapper">
        <div class="logo-title">GIGA</div>
      </div>
      <div class="logo-subtitle">Gestión Integral de Guardias y Asistencia</div>
    </a>
    <div class="navbar-right">
      <div class="organization-name">Subsecretaría de Seguridad Vial</div>
      <img alt="SsSV" class="SsSV" src="/logos/SsSV.png" />
    </div>
  </div>
</nav>

<style>
  .navbar {
    width: 100%;
    max-width: 100%;
    font-family: Verdana, Geneva, Tahoma, sans-serif;
    padding: 12px 0;
    background: linear-gradient(
      135deg,
      rgba(64, 123, 255, 0.85) 0%,
      rgba(44, 87, 199, 0.75) 100%
    );
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow:
      0 8px 32px rgba(64, 123, 255, 0.25),
      inset 0 -1px 2px rgba(255, 255, 255, 0.3),
      inset 0 1px 2px rgba(0, 0, 0, 0.1);
    overflow-x: hidden;
    box-sizing: border-box;
  }

  .navbar-container {
    max-width: 100%;
    width: 100%;
    margin: 0 auto;
    padding: 0 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    box-sizing: border-box;
  }

  @media (min-width: 768px) {
    .navbar-container {
      padding: 0 2rem;
      gap: 1.5rem;
    }
  }

  @media (min-width: 1024px) {
    .navbar-container {
      max-width: 1400px;
      padding: 0 2rem;
      gap: 1.5rem;
    }
  }

  .navbar-left {
    display: flex;
    flex-direction: column;
    gap: 4px;
    text-decoration: none;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 8px 12px;
    border-radius: 12px;
    background: linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.15) 0%,
      rgba(255, 255, 255, 0.08) 100%
    );
    box-shadow:
      0 4px 16px rgba(0, 0, 0, 0.15),
      inset 0 1px 2px rgba(255, 255, 255, 0.25),
      inset 0 -1px 2px rgba(0, 0, 0, 0.1);
    flex-shrink: 1;
    min-width: 0;
  }

  @media (min-width: 768px) {
    .navbar-left {
      padding: 12px 24px;
      border-radius: 20px;
    }
  }

  .navbar-left:hover {
    box-shadow:
      0 6px 20px rgba(0, 0, 0, 0.2),
      0 0 16px rgba(64, 123, 255, 0.2),
      inset 0 1px 2px rgba(255, 255, 255, 0.35),
      inset 0 -1px 2px rgba(0, 0, 0, 0.15);
    transform: translateY(-1px);
  }

  .logo-title-wrapper {
    position: relative;
    display: inline-block;
    overflow: hidden;
  }

  .logo-title {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: #e8f1ff;
    text-shadow:
      0 2px 4px rgba(0, 0, 0, 0.3),
      0 0 12px rgba(64, 123, 255, 0.4);
    position: relative;
    display: inline-block;
    white-space: nowrap;
  }

  @media (min-width: 640px) {
    .logo-title {
      font-size: 24px;
      letter-spacing: 0.8px;
    }
  }

  @media (min-width: 1024px) {
    .logo-title {
      font-size: 30px;
      letter-spacing: 1px;
    }
  }

  .logo-title-wrapper::after {
    content: "";
    position: absolute;
    width: 35%;
    height: 2px;
    bottom: 0;
    left: -35%;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.9),
      transparent
    );
    opacity: 0;
    transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .navbar-left:hover .logo-title-wrapper::after {
    opacity: 1;
    animation: moveLine 2s linear infinite;
  }

  @keyframes moveLine {
    0% {
      left: -35%;
    }
    100% {
      left: 100%;
    }
  }

  .logo-subtitle {
    font-size: 9px;
    font-weight: 600;
    color: #e8f1ff;
    opacity: 0.85;
    letter-spacing: 0.3px;
    text-transform: uppercase;
    text-shadow:
      0 2px 4px rgba(0, 0, 0, 0.3),
      0 0 8px rgba(64, 123, 255, 0.3);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  @media (min-width: 640px) {
    .logo-subtitle {
      font-size: 11px;
      letter-spacing: 0.4px;
    }
  }

  @media (min-width: 1024px) {
    .logo-subtitle {
      font-size: 15px;
      letter-spacing: 0.5px;
    }
  }

  .navbar-right {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    flex-shrink: 0;
  }

  @media (min-width: 768px) {
    .navbar-right {
      gap: 16px;
      padding: 12px 24px;
    }
  }

  .organization-name {
    font-size: 11px;
    font-weight: 700;
    color: #e8f1ff;
    letter-spacing: 0.2px;
    text-shadow:
      0 2px 4px rgba(0, 0, 0, 0.3),
      0 0 12px rgba(64, 123, 255, 0.4);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 150px;
  }

  @media (min-width: 640px) {
    .organization-name {
      font-size: 13px;
      max-width: 200px;
    }
  }

  @media (min-width: 1024px) {
    .organization-name {
      font-size: 20px;
      letter-spacing: 0.3px;
      max-width: none;
    }
  }

  .SsSV {
    height: 40px;
    width: auto;
    filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3)) brightness(1.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  @media (min-width: 640px) {
    .SsSV {
      height: 48px;
    }
  }

  @media (min-width: 1024px) {
    .SsSV {
      height: 56px;
    }
  }

  @media (max-width: 480px) {
    .organization-name {
      display: none;
    }
  }

  /* Aggressive mobile optimization for navbar */
  @media (max-width: 640px) {
    .navbar {
      padding: 4px 0;
      position: relative;
    }

    .navbar-container {
      padding: 0 0.5rem;
      gap: 0.5rem;
    }

    .navbar-left {
      padding: 4px 8px;
      gap: 2px;
    }

    .logo-title {
      font-size: 16px;
      letter-spacing: 0.3px;
    }

    .logo-subtitle {
      font-size: 8px;
      letter-spacing: 0.2px;
    }

    .navbar-right {
      padding: 4px 6px;
      gap: 6px;
    }

    .SsSV {
      height: 32px;
    }
  }

</style>
