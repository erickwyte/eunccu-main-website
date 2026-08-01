document.addEventListener('DOMContentLoaded', function () {
  const tabLinks = document.querySelectorAll('.tab-link');
  const tabContents = document.querySelectorAll('.tab-content');

  tabLinks.forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      const target = this.getAttribute('data-tab');

      // Deactivate all links
      tabLinks.forEach(l => l.classList.remove('active'));

      // Hide all tab contents
      tabContents.forEach(content => content.style.display = 'none');

      // Activate clicked link and show target content
      this.classList.add('active');
      const targetContent = document.getElementById(target);
      if (targetContent) {
        targetContent.style.display = 'block';
      }
    });
  });
});
