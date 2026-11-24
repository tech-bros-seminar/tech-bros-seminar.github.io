"""Regression checks for resolving overlapping problem numbers across notebooks."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('site_builder', ROOT / 'scripts/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class NotebookTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'content/catalog.json').read_text())
        self.dniester = next(p for p in self.data['problems'] if p.get('notebook') == 'dniester')

    def test_sources_follow_the_problem_in_all_rendered_outputs(self):
        # Simulate the same printed number appearing in different collections.
        # Use an isolated build containing one AI paper and a synthetic human review.
        other = copy.deepcopy(self.data['problems'][0])
        other.update(number=self.dniester['number'], slug='kourovka-test')
        self.dniester['pdf_page'] = 7
        preprint = copy.deepcopy(self.data['preprints'][0])
        preprint['problem_slug'] = self.dniester['slug']
        self.data.update(problems=[other, self.dniester], preprints=[preprint])
        reviewed = dict(preprint, slug='test-human-version', reviewed_by=['Fixture reviewer'],
                        reviewed_at=preprint['published_at'], status='reviewed')
        self.data['solutions'] = [reviewed]
        label = 'Dniester ' + self.dniester['number']
        self.assertIn(label, build.preprint_page(self.data, preprint))
        self.assertIn(label, build.solution_page(self.data, reviewed))
        self.assertIn('Kourovka ' + other['number'], build.home(self.data))
        for page in (build.home(self.data), build.problem_page(self.data, self.dniester, other)):
            self.assertIn(label, page)
        source = self.data['notebooks']['dniester']
        self.assertIn(build.esc(source['url']+'#page=7'), build.preprint_page(self.data, preprint))
        self.data.update(solutions=[], preprints=[])
        other['status']='under_investigation'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'assets').mkdir()
            (root/'content').mkdir()
            (root/'content/catalog.json').write_text(json.dumps(self.data))
            build.build(root)
            md = (root/'dist/downloads'/f"{self.dniester['slug']}.md").read_text()
            self.assertIn(label, md)
            self.assertIn(source['url']+'#page=7', md)
            self.assertNotIn('Kourovka', md)

    def test_unknown_and_mismatched_sources_are_rejected(self):
        for notebook in ('missing', 'kourovka', None):
            with self.subTest(notebook=notebook):
                self.dniester['notebook'] = notebook
                with self.assertRaises(ValueError):
                    build.validate_catalog(self.data)
