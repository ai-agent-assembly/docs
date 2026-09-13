(function () {
  'use strict';
  // The generated 404 keeps the requested URL; derive only a validated module
  // root from the publishing manifest, never invent an equivalent article.
  var script = document.currentScript;
  var root = script ? new URL('../', script.src) : new URL('/', document.baseURI);
  if (document.documentElement.lang === 'zh-Hant' && root.pathname.endsWith('/zh-Hant/')) {
    root = new URL('../', root);
  }

  function init() {
    var heading = document.getElementById('document-not-found-404');
    if (!heading) return;
    document.body.classList.add('aa-missing-document');
    document.querySelectorAll('.aa-feedback').forEach(function (node) { node.remove(); });
    var paragraph = document.createElement('p');
    paragraph.className = 'aa-recovery-context';
    var link = document.createElement('a');
    link.href = root.href;
    link.textContent = 'Back to Docs Hub';
    paragraph.appendChild(link);
    (heading.nextElementSibling || heading).after(paragraph);

    fetch(new URL('modules.json', root), {cache: 'no-cache'})
      .then(function (response) {
        if (!response.ok) { throw new Error('No module manifest'); }
        return response.json();
      })
      .then(function (data) {
        var relative = location.pathname.startsWith(root.pathname)
          ? location.pathname.slice(root.pathname.length) : '';
        var segment = relative.split('/')[0];
        var modules = Array.isArray(data.modules) ? data.modules : [];
        var module = modules.find(function (candidate) {
          return candidate && /^[a-z0-9][a-z0-9-]*$/.test(candidate.subpath)
            && candidate.subpath === segment && typeof candidate.name === 'string';
        });
        if (!module) return;
        var name = module.subpath === 'core' ? 'Core' : module.name
          .replace(/(^|[-_])([a-z])/g, function (_, separator, letter) { return (separator ? ' ' : '') + letter.toUpperCase(); })
          .replace(/\bSdk\b/g, 'SDK');
        link.href = new URL(module.subpath + '/', root).href;
        link.textContent = 'Back to ' + name + ' docs';

        function selectContext() {
          var selector = document.querySelector('.aa-modswitch__mod');
          if (!selector || !Array.from(selector.options).some(function (option) { return option.value === module.subpath; })) return false;
          selector.value = module.subpath;
          selector.dispatchEvent(new Event('change', {bubbles: true}));
          document.body.classList.add('aa-recovery-context-ready');
          return true;
        }
        if (selectContext()) return;
        var observer = new MutationObserver(function () { if (selectContext()) observer.disconnect(); });
        observer.observe(document.body, {childList: true, subtree: true});
        window.addEventListener('pagehide', function () { observer.disconnect(); }, {once: true});
      })
      .catch(function () { /* The explicit Hub recovery remains useful offline. */ });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
  else init();
})();
