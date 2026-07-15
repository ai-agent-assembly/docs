// AI Agent Assembly docs — adoption-funnel GA4 events (HORO-48).
//
// Fires the docs_* events defined in the internal event-taxonomy (§2.5) and
// tags every hit with the surface parameters required by §3.1
// (`hostname`, `page_path`, `page_title`, `surface='docs'`).
//
// Consent Mode v2 is already initialised in head.hbs: gtag() calls made
// here are queued while `analytics_storage` is denied and only flushed
// after the visitor accepts. No PII is emitted — every parameter value is
// either a coarse taxonomy tag (`command_type`, `sdk`, `cta_location`,
// `target_product`) or a stable page identifier (`page_path`, `page_title`).
(function () {
  'use strict';

  const SURFACE = 'docs';
  const GITHUB_CORE = 'github.com/ai-agent-assembly/agent-assembly';
  const GITHUB_EXAMPLES = 'github.com/ai-agent-assembly/examples';
  const GITHUB_ISSUE_ANY = /^https?:\/\/github\.com\/ai-agent-assembly\/[^/]+\/issues/;

  function baseParams() {
    return {
      hostname: location.hostname,
      page_path: location.pathname,
      page_title: document.title,
      surface: SURFACE
    };
  }

  function fire(name, extra) {
    if (typeof window.gtag !== 'function') { return; }
    const params = baseParams();
    if (extra) {
      for (const k in extra) {
        if (Object.prototype.hasOwnProperty.call(extra, k)) { params[k] = extra[k]; }
      }
    }
    window.gtag('event', name, params);
  }

  // Expose a small helper for pages that want to fire custom docs events.
  window.aaTrackDocsEvent = fire;

  // -----------------------------------------------------------------
  // Page-view classification events. Runs once per page load.
  // -----------------------------------------------------------------
  function firePageViewEvents() {
    const path = location.pathname;

    if (/(^|\/)security-model(\.html)?$/.test(path)) {
      fire('docs_security_model_view');
    }
    if (/(^|\/)(quickstart-saas|installation)(\.html)?$/.test(path)) {
      fire('docs_installation_view');
    }
    // SDK page views — the aggregated module docs live under /python-sdk/,
    // /node-sdk/, /go-sdk/. Fire once when the reader lands on any page
    // under that subpath so the report can attribute intent by language.
    if (/^\/python-sdk\//.test(path)) {
      fire('docs_sdk_python_view', { sdk: 'python' });
    } else if (/^\/node-sdk\//.test(path)) {
      fire('docs_sdk_node_view', { sdk: 'node' });
    } else if (/^\/go-sdk\//.test(path)) {
      fire('docs_sdk_go_view', { sdk: 'go' });
    }
  }

  // -----------------------------------------------------------------
  // CTA / outbound-click classification. One delegated listener.
  // -----------------------------------------------------------------
  function ctaLocationFor(a) {
    // Explicit override wins.
    const explicit = a.getAttribute('data-cta-location');
    if (explicit) { return explicit; }
    if (a.closest('.aa-cta-next')) { return 'body'; }
    if (a.closest('nav, .sidebar, .chapter')) { return 'nav'; }
    if (a.closest('footer')) { return 'footer'; }
    return 'body';
  }

  function targetProductFor(url) {
    if (/github\.com/.test(url)) { return 'github'; }
    if (/agent-assembly\.com\/early-access/.test(url)) { return 'early_access'; }
    if (/agent-assembly\.com/.test(url)) { return 'agent_assembly'; }
    if (/horonomy\.dev/.test(url)) { return 'horonomy'; }
    return 'docs';
  }

  function commandTypeFor(text) {
    if (!text) { return 'other'; }
    const t = text.trim().toLowerCase();
    if (t.indexOf('brew ') === 0) { return 'brew'; }
    if (t.indexOf('docker') !== -1) { return 'docker'; }
    if (t.indexOf('curl ') === 0 || t.indexOf('curl -') !== -1) { return 'curl'; }
    if (t.indexOf('pip ') === 0 || t.indexOf('pnpm ') === 0 || t.indexOf('npm ') === 0 ||
        t.indexOf('yarn ') === 0 || t.indexOf('go ') === 0 || t.indexOf('cargo ') === 0) {
      return 'source';
    }
    return 'other';
  }

  function handleAnchorClick(e) {
    const a = e.target?.closest?.('a[href]');
    if (!a) { return; }
    const href = a.getAttribute('href') || '';
    if (!href || href.charAt(0) === '#') { return; }

    const params = {
      cta_location: ctaLocationFor(a),
      link_url: a.href,
      link_domain: a.hostname || '',
      target_product: targetProductFor(a.href)
    };

    // Explicit event override for hand-tagged CTAs (Quickstart-next-step, etc.).
    const explicitEvent = a.getAttribute('data-track-event');
    if (explicitEvent) {
      fire(explicitEvent, params);
      return;
    }

    // Auto-classify by destination.
    if (a.href.indexOf(GITHUB_EXAMPLES) !== -1) {
      fire('docs_examples_click', params);
      return;
    }
    if (GITHUB_ISSUE_ANY.test(a.href)) {
      fire('docs_github_issue_click', params);
      return;
    }
    if (a.href.indexOf(GITHUB_CORE) !== -1) {
      fire('github_core_repo_click', params);
      return;
    }
    if (/agent-assembly\.com\/early-access/.test(a.href)) {
      fire('cta_cloud_early_access_click', params);
      return;
    }
  }

  // -----------------------------------------------------------------
  // Copy-to-clipboard on install commands. mdBook renders a `.clip-button`
  // inside every `pre > code` — hook the click and infer the command type
  // from the code text (Section 3.3 closed vocabulary).
  // -----------------------------------------------------------------
  function isInstallPage() {
    const path = location.pathname;
    return /(^|\/)(quickstart-saas|installation)(\.html)?$/.test(path);
  }

  function handleCopyClick(e) {
    if (!isInstallPage()) { return; }
    const btn = e.target?.closest?.('.clip-button, button[aria-label="Copy to clipboard"]');
    if (!btn) { return; }
    const pre = btn.closest('pre');
    const code = pre?.querySelector('code');
    const text = code ? code.textContent : '';
    fire('docs_copy_install_command', {
      cta_location: 'install_block',
      command_type: commandTypeFor(text)
    });
  }

  // -----------------------------------------------------------------
  // Boot
  // -----------------------------------------------------------------
  function init() {
    firePageViewEvents();
    document.addEventListener('click', handleAnchorClick, true);
    document.addEventListener('click', handleCopyClick, true);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
