<footer class="footer">
  <div class="footer-container">
    <div class="footer-left">
      <img alt="PC" class="footer-logo" src="/logos/PC.png" />
      <div class="department-name">Subsecretaría de Protección Civil</div>
    </div>
    <div class="footer-right">
      <div class="footer-info">2025 - UNTDF - Ushuaia - Tierra del Fuego</div>
    </div>
  </div>
</footer>

<style>
  .footer {
    width: 100vw;
    max-width: 100%;
    margin-top: auto;
    font-family: Verdana, Geneva, Tahoma, sans-serif;
    padding: 12px 0;
    background: linear-gradient(135deg, 
      rgba(64, 123, 255, 0.85) 0%, 
      rgba(44, 87, 199, 0.75) 100%);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 
      0 -8px 32px rgba(64, 123, 255, 0.25),
      inset 0 1px 2px rgba(255, 255, 255, 0.3),
      inset 0 -1px 2px rgba(0, 0, 0, 0.1);
    position: relative;
    left: 0;
    right: 0;
    overflow-x: hidden;
  }

  .footer-container {
    max-width: 100%;
    width: 100%;
    margin: 0 auto;
    padding: 0 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
    box-sizing: border-box;
  }

  @media (min-width: 768px) {
    .footer-container {
      padding: 0 2rem;
      gap: 2rem;
    }
  }

  @media (min-width: 1024px) {
    .footer-container {
      max-width: 1400px;
    }
  }

  .footer-left {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 0;
    flex-shrink: 1;
    min-width: 0;
  }

  @media (min-width: 768px) {
    .footer-left {
      gap: 16px;
      padding: 12px 0;
    }
  }

  .footer-logo {
    height: 40px;
    width: auto;
    filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3)) brightness(1.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  @media (min-width: 640px) {
    .footer-logo {
      height: 48px;
    }
  }

  @media (min-width: 1024px) {
    .footer-logo {
      height: 60px;
    }
  }

  .department-name {
    font-size: 11px;
    font-weight: 700;
    color: #E8F1FF;
    letter-spacing: 0.2px;
    text-shadow: 
      0 2px 4px rgba(0, 0, 0, 0.3),
      0 0 12px rgba(64, 123, 255, 0.4);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  @media (min-width: 640px) {
    .department-name {
      font-size: 13px;
    }
  }

  @media (min-width: 1024px) {
    .department-name {
      font-size: 20px;
      letter-spacing: 0.3px;
    }
  }

  .footer-right {
    display: flex;
    align-items: center;
    padding: 8px 0;
    flex-shrink: 0;
  }

  @media (min-width: 768px) {
    .footer-right {
      padding: 12px 0;
    }
  }

  .footer-info {
    font-size: 10px;
    font-weight: 600;
    color: #E8F1FF;
    letter-spacing: 0.3px;
    text-shadow: 
      0 2px 4px rgba(0, 0, 0, 0.3),
      0 0 12px rgba(64, 123, 255, 0.4);
    white-space: nowrap;
  }

  @media (min-width: 640px) {
    .footer-info {
      font-size: 12px;
      letter-spacing: 0.4px;
    }
  }

  @media (min-width: 1024px) {
    .footer-info {
      font-size: 18px;
      letter-spacing: 0.5px;
    }
  }

  @media (max-width: 640px) {
    .footer-container {
      flex-direction: column;
      gap: 0.75rem;
      text-align: center;
    }

    .footer-left,
    .footer-right {
      justify-content: center;
      width: 100%;
    }

    .footer-left {
      flex-direction: column;
      gap: 8px;
    }
  }
</style>
