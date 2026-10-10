# Contributing to al-folio
Thank you for considering to contribute to al-folio!


## Pull Requests
We welcome your pull requests (PRs).
For minor fixes (e.g., documentation improvements), feel free to submit a PR directly.
If you would like to implement a new feature or a bug, please make sure you (or someone else) has opened an appropriate issue first; in your PR, please mention the issue it addresses.


## Research homepage

The homepage uses `_layouts/research.html` and the introduction in
`_pages/about.md`. Its isolated stylesheet is `assets/css/research/home.css`,
and interactions live in `assets/js/research.js`. The nested CSS directory keeps
interactive states outside the legacy theme's PurgeCSS glob. The JavaScript is
excluded from the legacy minifier to preserve native dialog behavior.

Publication metadata comes from `_bibliography/papers.bib`. Edit
`_data/research_publications.json` for topic tags, takeaways, summaries, and
`featured_order`; omit that field to keep a paper archive-only. New bibliography
entries appear in the archive automatically. Figures belong in
`assets/img/publication_preview/`. The latest three `_news/` entries appear on
the homepage.

Python 3 is required alongside Ruby: `_plugins/research_publications.rb` invokes
`bin/render_research.py` during both `jekyll build` and `jekyll serve`. The renderer
uses only the Python standard library and accepts the repository's braced
`@article` fields. No manual generation or committed generated HTML is needed.

Before committing, run `python3 bin/test_research.py`,
`node --check assets/js/research.js`, and `bundle exec jekyll build --lsi`.
Check mobile and desktop layouts, both themes, topic filters, and figure previews
(including Escape, Tab, and focus restoration). Sharing metadata uses `site.url`
and `site.baseurl`; its image is `assets/social-preview.png`.

## Issues
We use GitHub issues to track bugs and feature requests.
Before submitting an issue, please make sure:

1. You have read [the FAQ section](https://github.com/alshedivat/al-folio#faq) of the README and your question is NOT addressed there.
2. You have done your best to ensure that your issue is NOT a duplicate of one of [the previous issues](https://github.com/alshedivat/al-folio/issues).
3. Your issue is either a bug (unexpected/undesirable behavior) or a feature request.
If it is just a question, please ask it in the [Discussions](https://github.com/alshedivat/al-folio/discussions) forum.

When submitting an issue, please make sure to use the appropriate template.


## License
By contributing to al-folio, you agree that your contributions will be licensed
under the LICENSE file in the root directory of the source tree.
