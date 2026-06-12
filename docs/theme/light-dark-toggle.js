// AI Agent Assembly — visible light/dark toggle for the mdBook menu bar.
//
// mdBook 0.5.x ships a paintbrush theme picker (#mdbook-theme-toggle) that opens
// a popup, but it is easy to miss. This adds an always-visible sun/moon button
// to the menu bar that flips between the light and dark themes by delegating to
// mdBook's own bundled theme menu items, so persistence (localStorage
// `mdbook-theme`) and class handling are inherited for free.

(function () {
    'use strict';

    var DARK_THEMES = ['navy', 'coal', 'ayu'];
    var MOON = '☾'; // ☾  shown in light mode (click -> go dark)
    var SUN = '☀';  // ☀  shown in dark mode (click -> go light)

    function isDark() {
        var classes = document.documentElement.classList;
        for (var i = 0; i < DARK_THEMES.length; i++) {
            if (classes.contains(DARK_THEMES[i])) {
                return true;
            }
        }
        return false;
    }

    function ready(fn) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', fn);
        } else {
            fn();
        }
    }

    ready(function () {
        var leftButtons = document.querySelector('.left-buttons');
        var lightItem = document.getElementById('mdbook-theme-light');
        var darkItem = document.getElementById('mdbook-theme-navy');

        // Defensive: if mdBook's menu bar or theme items are missing, do nothing.
        if (!leftButtons || !lightItem || !darkItem) {
            return;
        }

        var button = document.createElement('button');
        button.id = 'aaasm-light-dark-toggle';
        button.type = 'button';
        button.className = 'icon-button';
        button.setAttribute('aria-label', 'Toggle light/dark mode');
        button.setAttribute('title', 'Toggle light/dark mode');

        var glyph = document.createElement('span');
        glyph.setAttribute('aria-hidden', 'true');
        button.appendChild(glyph);

        function refreshGlyph() {
            var dark = isDark();
            glyph.textContent = dark ? SUN : MOON;
            button.setAttribute(
                'title',
                dark ? 'Switch to light mode' : 'Switch to dark mode'
            );
        }

        button.addEventListener('click', function () {
            // Click mdBook's own menu item so book.js handles persistence and
            // class application; flip relative to the current theme.
            if (isDark()) {
                lightItem.click();
            } else {
                darkItem.click();
            }
            // book.js applies the class synchronously on click; reflect it.
            refreshGlyph();
        });

        // Insert next to the paintbrush theme toggle when present.
        var paintbrush = document.getElementById('mdbook-theme-toggle');
        if (paintbrush && paintbrush.parentNode === leftButtons) {
            leftButtons.insertBefore(button, paintbrush.nextSibling);
        } else {
            leftButtons.appendChild(button);
        }

        // Keep the glyph in sync if the theme is changed elsewhere (paintbrush
        // menu, system preference change, another tab).
        var observer = new MutationObserver(refreshGlyph);
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['class'],
        });

        refreshGlyph();
    });
})();
