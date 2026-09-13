// Shared, dependency-free URL helpers for the hub's rendered search and
// module switcher. Keeping these pure lets their source contracts be tested
// without executing template text as code.
(function (root) {
  function canonical(raw, href, origin) {
    try {
      var url = new URL(raw, href);
      if (url.origin !== origin) { return null; }
      url.search = '';
      url.pathname = url.pathname.replace(/\/index\.html$/, '/');
      return url;
    } catch (e) { return null; }
  }
  function scope(url) {
    var parts = url.pathname.split('/').filter(Boolean);
    var names = { core: 'Core', 'python-sdk': 'Python SDK', 'node-sdk': 'Node SDK',
      'go-sdk': 'Go SDK', arena: 'Arena' };
    for (var i = 0; i < parts.length; i++) {
      if (names[parts[i]]) {
        var channel = parts[i + 1] || 'default';
        if (parts[i] === 'node-sdk') {
          if (channel === 'next') { channel = 'latest (main)'; }
          else if (!/^v?\d/.test(channel)) { channel = 'default'; }
        }
        return names[parts[i]] + ' · ' + channel;
      }
    }
    return 'Hub · English';
  }
  function moduleRoot(baseURI, pathToRoot, language) {
    var result = new URL(pathToRoot || './', baseURI);
    if (language === 'zh-Hant') { result = new URL('../', result); }
    return result.href;
  }
  root.AADocsUtils = Object.freeze({ canonical: canonical, scope: scope, moduleRoot: moduleRoot });
})(globalThis);
