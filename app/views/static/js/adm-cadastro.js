document.addEventListener("DOMContentLoaded", function () {
  const menuItems = document.querySelectorAll('.item-menu, .item-menu-blue');
  const contentArea = document.getElementById('content-cad');

  menuItems.forEach(item => {
      const page = item.getAttribute('data-page');

      if (page) {
          item.style.cursor = 'pointer';
          item.addEventListener('click', () => {
              fetch(page)
                  .then(response => {
                      if (!response.ok) {
                          throw new Error('Erro ao carregar a página: ' + page);
                      }
                      return response.text();
                  })
                  .then(html => {
                      contentArea.innerHTML = html;
                      window.scrollTo(0, 0); // opcional: rola pro topo ao carregar
                  })
                  .catch(error => {
                      contentArea.innerHTML = `<p style="color: red;">Erro ao carregar o conteúdo.</p>`;
                      console.error(error);
                  });
          });
      }
  });
});
