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
    position: sticky;
    top: 0;
    width: 100%;
    z-index: 1000;
    font-family: Verdana, Geneva, Tahoma, sans-serif;
    padding: 12px 0;
    background: linear-gradient(135deg, 
      rgba(64, 123, 255, 0.85) 0%, 
      rgba(44, 87, 199, 0.75) 100%);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 
      0 8px 32px rgba(64, 123, 255, 0.25),
      inset 0 -1px 2px rgba(255, 255, 255, 0.3),
      inset 0 1px 2px rgba(0, 0, 0, 0.1);
  }

  .navbar-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 24px;
  }

  .navbar-left {
    display: flex;
    flex-direction: column;
    gap: 4px;
    text-decoration: none;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 12px 24px;
    border-radius: 20px;
    background: linear-gradient(135deg, 
      rgba(255, 255, 255, 0.15) 0%, 
      rgba(255, 255, 255, 0.08) 100%);
    box-shadow: 
      0 4px 16px rgba(0, 0, 0, 0.15),
      inset 0 1px 2px rgba(255, 255, 255, 0.25),
      inset 0 -1px 2px rgba(0, 0, 0, 0.1);
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
    font-size: 30px;
    font-weight: 800;
    letter-spacing: 1px;
    color: #E8F1FF;
    text-shadow: 
      0 2px 4px rgba(0, 0, 0, 0.3),
      0 0 12px rgba(64, 123, 255, 0.4);
    position: relative;
    display: inline-block;
  }

  .logo-title-wrapper::after {
    content: "";
    position: absolute;
    width: 35%;
    height: 2px;
    bottom: 0;
    left: -35%;
    background: linear-gradient(90deg, 
      transparent, 
      rgba(255, 255, 255, 0.9), 
      transparent);
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
    font-size: 15px;
    font-weight: 600;
    color: #E8F1FF;
    opacity: 0.85;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    text-shadow: 
      0 2px 4px rgba(0, 0, 0, 0.3),
      0 0 8px rgba(64, 123, 255, 0.3);
  }

  .navbar-right {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px 24px;
  }

  .organization-name {
    font-size: 20px;
    font-weight: 700;
    color: #E8F1FF;
    letter-spacing: 0.3px;
    text-shadow: 
      0 2px 4px rgba(0, 0, 0, 0.3),
      0 0 12px rgba(64, 123, 255, 0.4);
  }

  .SsSV {
    height: 56px;
    width: auto;
    filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3)) brightness(1.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .SsSV:hover {
    filter: drop-shadow(0 6px 16px rgba(255, 255, 255, 0.4)) brightness(1.2);
    transform: scale(1.05);
  }

  @media (max-width: 1024px) {
    .navbar-container {
      padding: 0 24px;
    }

    .logo-title {
      font-size: 24px;
    }

    .logo-subtitle {
      font-size: 11px;
    }

    .organization-name {
      font-size: 13px;
    }

    .SsSV {
      height: 48px;
    }
  }

  @media (max-width: 768px) {
    .navbar-container {
      flex-direction: column;
      gap: 16px;
      padding: 0 16px;
    }

    .navbar-left,
    .navbar-right {
      width: 100%;
      justify-content: center;
      text-align: center;
    }

    .logo-subtitle {
      font-size: 10px;
    }
  }
</style>
