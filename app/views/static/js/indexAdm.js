function ativarLinks() {
    // Para links no offcanvas
    document.querySelectorAll('[data-link]').forEach(link => {
      link.addEventListener('click', function (event) {
        event.preventDefault();
        const url = this.getAttribute('href');
  
        fetch(url)
          .then(response => response.text())
          .then(html => {
            document.getElementById('content').innerHTML = html;
            ativarLinks(); // reativa os eventos após carregar novo conteúdo
          })
          .catch(error => {
            document.getElementById('content').innerHTML = '<p>Erro ao carregar conteúdo.</p>';
            console.error(error);
          });
      });
    });
  
    // Para os cards do menu
    document.querySelectorAll('[data-page]').forEach(item => {
      item.addEventListener('click', () => {
        const page = item.getAttribute('data-page');
  
        fetch(page)
          .then(response => response.text())
          .then(html => {
            document.getElementById('content').innerHTML = html;
            ativarLinks(); // reativa os eventos após carregar novo conteúdo
          })
          .catch(() => {
            document.getElementById('content').innerHTML = '<p>Erro ao carregar a página.</p>';
          });
      });
    });
  
    // Para restaurar conteúdo inicial ao clicar em "SAEC"
    const homeTemplate = document.getElementById('home-template');
    const logo = document.querySelector('.navbar-brand');
    if (logo && homeTemplate) {
      logo.addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('content').innerHTML = homeTemplate.innerHTML;
        ativarLinks(); // reativa os eventos no conteúdo restaurado
      });
    }
  }
  
  // Ativa ao carregar a página e exibe o conteúdo inicial
  document.addEventListener('DOMContentLoaded', () => {
    const homeTemplate = document.getElementById('home-template');
    const content = document.getElementById('content');
  
    if (homeTemplate && content) {
      content.innerHTML = homeTemplate.innerHTML;
    }
  
    ativarLinks();
  });
  