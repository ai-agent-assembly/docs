/* Distinguish mdBook's native search from the separate aggregated search. */
(function () {
  function labelLocalSearch() {
    var label = document.documentElement.lang.indexOf('zh') === 0 ? '搜尋本書' : 'Search this book';
    var toggle = document.getElementById('search-toggle');
    if (toggle) {
      toggle.setAttribute('aria-label', label);
      toggle.setAttribute('title', label);
    }
    var input = document.getElementById('searchbar');
    if (input) input.setAttribute('aria-label', label);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', labelLocalSearch, {once: true});
  } else {
    labelLocalSearch();
  }
})();
