(function(){
  function loadTinyMCE(){
    if (typeof tinymce === 'undefined') { return; }
    var selectors = [];
    if (document.getElementById('id_content')) selectors.push('#id_content');
    if (document.getElementById('id_summary')) selectors.push('#id_summary');
    if (document.getElementById('id_description')) selectors.push('#id_description');
    if (!selectors.length) return;

    tinymce.init({
      selector: selectors.join(','),
      menubar: false,
      plugins: 'link lists code table paste',
      toolbar: 'undo redo | styles | bold italic underline | bullist numlist | link | alignleft aligncenter alignright | table | code',
      height: 300,
      branding: false,
      paste_as_text: true
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadTinyMCE);
  } else {
    loadTinyMCE();
  }
})();
