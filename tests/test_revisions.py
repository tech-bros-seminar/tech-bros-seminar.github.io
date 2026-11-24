"""A revision should move the current solution link while keeping old URLs usable."""
import copy
import json
import unittest

import test_publication_gate as fixtures


class RevisionTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.PublicationGateTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.root = fixture.root
        self.catalogue = fixture.with_preprint()
        self.problem = self.catalogue['problems'][0]
        self.problem['status'] = 'proposed_solution_published'
        self.original = self.catalogue['preprints'][0]
        self.revision = copy.deepcopy(self.original)
        self.revision.update(slug='shorter-proof-v2', version='2',
                             revises=self.original['slug'],
                             revision_summary='Eliminates the finiteness assumption.')
        for field in ('proof_file', 'review_file', 'source_file'):
            old_path = self.original[field]
            new_path = old_path.replace('v1', 'v2')
            (self.root / 'content' / new_path).write_text('Revision fixture.\n')
            self.revision[field] = new_path
        self.catalogue['preprints'].append(self.revision)

    def test_new_and_old_versions_survive_build(self):
        (self.root / 'content/catalog.json').write_text(json.dumps(self.catalogue))
        fixtures.build.build(self.root)
        dist = self.root / 'dist'
        old_url = f'/publications/{self.original["slug"]}/'
        new_url = f'/publications/{self.revision["slug"]}/'
        old_html = (dist / old_url.strip('/') / 'index.html').read_text()
        new_html = (dist / new_url.strip('/') / 'index.html').read_text()
        self.assertIn(f'href="{new_url}"', old_html)
        self.assertIn(f'href="{old_url}"', new_html)
        self.assertIn(self.revision['revision_summary'], new_html)
        self.assertEqual(fixtures.build.problem_destination(self.catalogue, self.problem), new_url)
        for paper, page in ((self.original, old_html), (self.revision, new_html)):
            self.assertIn(f'href="/{paper["proof_file"]}"', page)
            self.assertTrue((dist / paper['proof_file']).is_file())

    def test_rejects_broken_version_history(self):
        other = dict(self.problem, slug='other-problem', number='2', status='under_investigation')
        self.catalogue['problems'].append(other)
        for changes in [
            {'revises': 'missing'},
            {'revises': self.revision['slug']},
            {'problem_slug': other['slug']},
            {'revision_summary': '  '},
            {'version': self.original['version']},
            {'source_file': self.original['source_file']},
            {'review_file': self.original['review_file']},
        ]:
            with self.subTest(changes=changes):
                data = copy.deepcopy(self.catalogue)
                data['preprints'][-1].update(changes)
                with self.assertRaises(ValueError):
                    fixtures.build.validate_catalog(data, self.root)
