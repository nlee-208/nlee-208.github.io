"""Regression checks for bibliography-driven homepage rendering."""
import contextlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('renderer', Path(__file__).with_name('render_research.py'))
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class InspectHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class ResearchTests(unittest.TestCase):
    @contextlib.contextmanager
    def fixture(self, bib, notes=None):
        old_repo, old_baseurl = renderer.REPO, renderer.BASEURL
        with tempfile.TemporaryDirectory() as directory:
            renderer.REPO = Path(directory)
            (renderer.REPO / '_bibliography').mkdir()
            (renderer.REPO / '_data').mkdir()
            (renderer.REPO / '_bibliography/papers.bib').write_text(bib)
            (renderer.REPO / '_data/research_publications.json').write_text(json.dumps(notes or {}))
            try:
                yield
            finally:
                renderer.REPO, renderer.BASEURL = old_repo, old_baseurl

    def test_real_publications_and_assets(self):
        papers = renderer.read_bibliography(renderer.REPO / '_bibliography/papers.bib')
        output = renderer.render_publications()
        parsed = InspectHTML()
        parsed.feed(output)
        archive = [a for _, a in parsed.elements if 'data-topics' in a]
        self.assertEqual(len(archive), len(papers))
        self.assertNotIn('Equal contribution', output)
        self.assertNotIn('Co-first authors', output)
        self.assertIn('Seonghyeon Kim*, Chaeyun Jang*', output)
        cards = output.split('<details id="all-publications">')[0]
        self.assertNotIn('AlphaPO', cards)
        self.assertIn('No Pain, More Gain', cards)
        for tag, attrs in parsed.elements:
            if tag == 'img':
                self.assertTrue((renderer.REPO / attrs['src'].lstrip('/')).is_file())

    def test_new_paper_is_automatically_archived_and_escaped(self):
        bib = '@article{new, title={A {nested} title & <example>}, author={Lee, Noah}, year={2030}, journal={Preprint}, arxiv={arXiv:3001.00001}}'
        with self.fixture(bib):
            output = renderer.render_publications()
            self.assertIn('A {nested} title &amp; &lt;example&gt;', output)
            self.assertIn('1 paper ·', output)
            self.assertIn('3001.00001', output)
            self.assertNotIn('<article class="paper">', output)

    def test_baseurl_is_applied_to_figure_links(self):
        old = renderer.BASEURL
        try:
            renderer.BASEURL = '/preview'
            output = renderer.render_publications()
            self.assertIn('href="/preview/assets/img/publication_preview/im-mopd.png"', output)
            self.assertIn('src="/preview/assets/img/publication_preview/im-mopd.png"', output)
            self.assertIn('https://arxiv.org/abs/2609.34745', output)
        finally:
            renderer.BASEURL = old

    def test_invalid_notes_and_bibliography_fail_loudly(self):
        bib = '@article{new, title={Test}, year={2030}, journal={Preprint}, arxiv={arXiv:3001.00001}}'
        with self.fixture(bib, {'missing': {'topics': []}}):
            with self.assertRaisesRegex(ValueError, 'missing publications'):
                renderer.render_publications()
        with self.fixture(bib + '\n' + bib):
            with self.assertRaisesRegex(ValueError, 'Duplicate bibliography'):
                renderer.render_publications()
        with self.fixture(bib, {'new': {'topics': ['unknown']}}):
            with self.assertRaisesRegex(ValueError, 'Unknown topics'):
                renderer.render_publications()

    def test_author_order_and_shared_authorship(self):
        self.assertEqual(renderer.authors('Kim*, Seonghyeon and Jang*, Chaeyun and Lee, Noah'),
                         'Seonghyeon Kim*, Chaeyun Jang*, <strong>Noah Lee</strong>')


if __name__ == '__main__':
    unittest.main()
