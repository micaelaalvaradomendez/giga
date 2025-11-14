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
    width: 100%;
    margin-top: auto;
    font-family: Verdana, Geneva, Tahoma, sans-serif;
    padding: 2px 0;
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
  }

  .footer-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 32px;
    flex-wrap: wrap;
  }

  .footer-left {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 28px;
  }

  .footer-logo {
    height: 60px;
    width: auto;
    filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3)) brightness(1.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .department-name {
    font-size: 20px;
    font-weight: 700;
    color: #E8F1FF;
    letter-spacing: 0.3px;
    text-shadow: 
      0 2px 4px rgba(0, 0, 0, 0.3),
      0 0 12px rgba(64, 123, 255, 0.4);
  }

  .footer-right {
    display: flex;
    align-items: center;
    padding: 16px 28px;
  }

  .footer-info {
    font-size: 18px;
    font-weight: 600;
    color: #E8F1FF;
    letter-spacing: 0.5px;
    text-shadow: 
      0 2px 4px rgba(0, 0, 0, 0.3),
      0 0 12px rgba(64, 123, 255, 0.4);
  }

  @media (max-width: 1024px) {
    .footer-container {
      padding: 0 24px;
    }

    .department-name {
      font-size: 13px;
    }

    .footer-info {
      font-size: 12px;
    }

    .footer-logo {
      height: 48px;
    }
  }

  @media (max-width: 768px) {
    .footer {
      padding: 20px 0;
    }

    .footer-container {
      flex-direction: column;
      gap: 16px;
      padding: 0 16px;
    }

    .footer-left,
    .footer-right {
      width: 100%;
      justify-content: center;
    }

    .footer-left {
      flex-direction: column;
      text-align: center;
      gap: 12px;
    }

    .department-name {
      font-size: 12px;
    }

    .footer-info {
      font-size: 11px;
    }

    .footer-logo {
      height: 44px;
    }
  }
</style>
