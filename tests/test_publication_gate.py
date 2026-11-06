"""Focused checks of what may cross the public publication boundary.

Every proof, author and review created here is a synthetic test fixture. Tests
use an isolated temporary directory and never alter the real public catalogue.
"""
from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('math_lab_public_build', ROOT / 'scripts/build.py')
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)


class PublicationGateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='math-lab-publication-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'content/files').mkdir(parents=True)
        (self.root / 'assets').mkdir()
        # Real public problem descriptions may be reused; any existing real
        # publications are removed before constructing synthetic fixtures.
        self.catalogue = json.loads((ROOT / 'content/catalog.json').read_text(encoding='utf-8'))
        self.catalogue['problems'] = copy.deepcopy(self.catalogue['problems'][:1])
        self.catalogue['problems'][0]['status'] = 'under_investigation'
        self.catalogue['solutions'] = []
        self.catalogue.pop('preprints', None)
        self.proof = self.root / 'content/files/fixture-proof-v1.md'
        self.review = self.root / 'content/files/fixture-review-v1.txt'
        self.proof.write_text('# Synthetic fixture\n\nNot a mathematical proof.\n', encoding='utf-8')
        self.review.write_text('Synthetic fixture only; no real review asserted.\n', encoding='utf-8')
        self.solution = {
            'slug': 'synthetic-fixture-v1',
            'problem_slug': self.catalogue['problems'][0]['slug'],
            'title': 'Synthetic publication fixture',
            'scope': 'partial_result',
            'status': 'reviewed',
            'version': '1',
            'published_at': '2026-11-06',
            'authors': ['Synthetic Fixture Author'],
            'abstract': 'A fixture for testing the publication boundary, not research.',
            'statement': 'This is a synthetic test record only.',
            'proof_file': 'files/fixture-proof-v1.md',
            'review_file': 'files/fixture-review-v1.txt',
            'reviewed_by': ['Synthetic Fixture Reviewer'],
            'reviewed_at': '2026-11-06',
            'review_summary': 'Fixture metadata; no real mathematical review took place.',
            'release_approved_by': 'Synthetic Fixture Maintainer',
            'release_approved_at': '2026-11-06',
        }

    def with_solution(self):
        data = copy.deepcopy(self.catalogue)
        data['solutions'] = [copy.deepcopy(self.solution)]
        return data

    def with_preprint(self):
        source = self.root / 'content/files/fixture-preprint-v1.tex'
        source.write_text('% Synthetic proposed manuscript only.\n', encoding='utf-8')
        preprint = {
            key: copy.deepcopy(value)
            for key, value in self.solution.items()
            if key not in {'reviewed_by', 'reviewed_at'}
        }
        preprint.update({
            'slug': 'synthetic-preprint-v1',
            'title': 'Synthetic proposed manuscript fixture',
            'scope': 'full_solution',
            'status': 'review_pending',
            'manuscript_date': '2026-10-26',
            'authors': [],
            'attribution_note': 'Synthetic fixture with unspecified authorship; no real author asserted.',
            'source_file': 'files/fixture-preprint-v1.tex',
            'review_summary': 'Synthetic fixture; human acceptance is not recorded.',
        })
        data = copy.deepcopy(self.catalogue)
        data['preprints'] = [preprint]
        return data

    def test_prompt_links_accept_legacy_and_public_conversations(self):
        legacy = self.with_preprint()
        build.validate_catalog(legacy, self.root)
        first = {
            'label': 'Synthetic research conversation',
            'url': 'https://example.org/shared/synthetic-research',
        }
        second = {
            'label': 'Synthetic follow-up conversation',
            'url': 'https://chatgpt.com/share/synthetic-follow-up',
        }
        for links in [[], [first], [first, second]]:
            with self.subTest(links=links):
                data = self.with_preprint()
                data['preprints'][0]['prompt_links'] = copy.deepcopy(links)
                build.validate_catalog(data, self.root)

    def test_prompt_links_reject_invalid_records_and_urls(self):
        public_url = 'https://example.org/shared/synthetic-research'
        invalid = [
            None, '', {}, [None], ['Synthetic conversation'], [{}],
            [{'label': 'Synthetic conversation'}],
            [{'url': public_url}],
            [{'label': '', 'url': public_url}],
            [{'label': 1, 'url': public_url}],
            [{'label': 'Synthetic conversation', 'url': public_url,
              'private_notes': 'Synthetic unreleased fixture.'}],
        ]
        for url in [
            '', None, 1, 'http://example.org/shared/fixture',
            'javascript:alert("synthetic-fixture")',
            '/shared/fixture', '//example.org/shared/fixture',
            'https:///shared/fixture',
            'https://synthetic-user:synthetic-password@example.org/shared/fixture',
            'https://synthetic-user@example.org/shared/fixture',
            ' https://example.org/shared/fixture',
            'https://example.org/shared/fixture ',
            'https://example.org/shared/two words',
            'https://example.org/shared/\nfixture',
            'https://example.org/shared/\x00fixture',
            r'https://example.org\shared\fixture',
            'https://example.org:invalid/shared/fixture',
            'https://example.org:65536/shared/fixture',
        ]:
            invalid.append([{'label': 'Synthetic conversation', 'url': url}])
        for links in invalid:
            with self.subTest(links=links):
                data = self.with_preprint()
                data['preprints'][0]['prompt_links'] = links
                with self.assertRaises(ValueError):
                    build.validate_catalog(data, self.root)

    def test_prompt_history_renders_safely_and_without_dead_links(self):
        data = self.with_preprint()
        paper = data['preprints'][0]
        destination = f'/publications/{paper["slug"]}/#prompts'
        self.assertNotIn(destination, build.manuscript_links(paper, True))
        self.assertIn('id="prompts"', build.preprint_page(data, paper))

        paper['prompt_links'] = [{
            'label': 'Synthetic "<script>fixture</script>" & conversation',
            'url': 'https://example.org/shared/fixture?phase=1&view=full',
        }]
        build.validate_catalog(data, self.root)
        section = build.prompt_section(paper)
        self.assertIn(
            'Synthetic &quot;&lt;script&gt;fixture&lt;/script&gt;&quot; &amp; conversation',
            section,
        )
        self.assertNotIn('<script>', section)
        self.assertIn('https://example.org/shared/fixture?phase=1&amp;view=full', section)
        self.assertIn(destination, build.manuscript_links(paper, True))
        page = build.preprint_page(data, paper)
        self.assertIn('id="prompts"', page)
        self.assertIn('https://example.org/shared/fixture?phase=1&amp;view=full', page)

    def test_problem_destination_respects_status_scope_and_version(self):
        data = self.with_preprint()
        problem = data['problems'][0]
        ai_template = data['preprints'][0]

        def fixture(template, slug, version, published_at, *,
                    scope='full_solution', status=None):
            paper = copy.deepcopy(template)
            paper.update({
                'slug': slug, 'version': version, 'published_at': published_at,
                'release_approved_at': published_at, 'scope': scope,
            })
            if 'reviewed_at' in paper:
                paper['reviewed_at'] = published_at
            if status is not None:
                paper['status'] = status
            if paper['status'] == 'withdrawn':
                paper['withdrawal_reason'] = 'Synthetic withdrawal fixture.'
            return paper

        data['preprints'] = [
            fixture(ai_template, 'synthetic-ai-old', '99', '2026-11-05'),
            fixture(ai_template, 'synthetic-ai-v10', '10', '2026-11-06'),
            fixture(ai_template, 'synthetic-ai-v2', '2', '2026-11-06'),
            fixture(ai_template, 'synthetic-ai-partial', '11', '2026-11-07',
                    scope='partial_result'),
            fixture(ai_template, 'synthetic-ai-withdrawn', '12', '2026-11-08',
                    status='withdrawn'),
        ]
        data['solutions'] = [
            fixture(self.solution, 'synthetic-reviewed-old', '1', '2026-11-04'),
            fixture(self.solution, 'synthetic-reviewed-v2', '2', '2026-11-09'),
            fixture(self.solution, 'synthetic-reviewed-partial', '3', '2026-11-10',
                    scope='partial_result'),
            fixture(self.solution, 'synthetic-reviewed-withdrawn', '4', '2026-11-11',
                    status='withdrawn'),
        ]
        build.validate_catalog(data, self.root)
        self.assertEqual(
            build.problem_destination(data, problem),
            f'/problems/{problem["slug"]}/',
        )

        problem['status'] = 'proposed_solution_published'
        build.validate_catalog(data, self.root)
        self.assertEqual(
            build.problem_destination(data, problem),
            '/publications/synthetic-ai-v10/',
        )
        data['preprints'].reverse()
        self.assertEqual(
            build.problem_destination(data, problem),
            '/publications/synthetic-ai-v10/',
        )

        # A newer AI paper must not replace a Human reviewed destination.
        data['preprints'].append(
            fixture(ai_template, 'synthetic-ai-newest', '13', '2026-11-12')
        )
        problem['status'] = 'project_solution_published'
        build.validate_catalog(data, self.root)
        self.assertEqual(
            build.problem_destination(data, problem),
            '/publications/synthetic-reviewed-v2/',
        )

    def test_publication_type_must_match_its_review_category(self):
        categories = [
            ('preprints', self.with_preprint, 'ai_generated', 'human_reviewed'),
            ('solutions', self.with_solution, 'human_reviewed', 'ai_generated'),
        ]
        for collection, factory, expected, opposite in categories:
            with self.subTest(collection=collection, form='valid'):
                data = factory()
                data[collection][0]['publication_type'] = expected
                build.validate_catalog(data, self.root)
            for value in [opposite, '', None]:
                with self.subTest(collection=collection, invalid_type=value):
                    data = factory()
                    data[collection][0]['publication_type'] = value
                    with self.assertRaises(ValueError):
                        build.validate_catalog(data, self.root)

    def test_human_revision_links_same_problem_and_preserves_ai_proof(self):
        data = self.with_preprint()
        data['preprints'][0]['publication_type'] = 'ai_generated'
        revised_proof = self.root / 'content/files/fixture-human-v2.md'
        revised_proof.write_text('# Synthetic human-revision fixture only.\n', encoding='utf-8')
        human = copy.deepcopy(self.solution)
        human.update({
            'slug': 'synthetic-human-v2',
            'version': '2',
            'publication_type': 'human_reviewed',
            'proof_file': 'files/fixture-human-v2.md',
            'based_on': data['preprints'][0]['slug'],
        })
        data['solutions'] = [human]
        build.validate_catalog(data, self.root)

        for defect in ['unknown_original', 'human_original', 'different_problem', 'shared_proof']:
            with self.subTest(defect=defect):
                invalid = copy.deepcopy(data)
                revised = invalid['solutions'][0]
                if defect == 'unknown_original':
                    revised['based_on'] = 'missing-ai-original'
                elif defect == 'human_original':
                    revised['based_on'] = revised['slug']
                elif defect == 'different_problem':
                    other = copy.deepcopy(invalid['problems'][0])
                    other.update({'slug': 'synthetic-other-problem', 'number': 'synthetic-2'})
                    invalid['problems'].append(other)
                    revised['problem_slug'] = other['slug']
                else:
                    revised['proof_file'] = invalid['preprints'][0]['proof_file']
                with self.assertRaises(ValueError):
                    build.validate_catalog(invalid, self.root)

        # The direction of the relationship is human revision -> AI original.
        invalid = self.with_preprint()
        invalid['preprints'][0]['based_on'] = invalid['preprints'][0]['slug']
        with self.assertRaises(ValueError):
            build.validate_catalog(invalid, self.root)

    def test_lean_status_must_be_nonempty_text_when_supplied(self):
        for collection, factory in [('preprints', self.with_preprint), ('solutions', self.with_solution)]:
            with self.subTest(collection=collection, form='valid'):
                data = factory()
                data[collection][0]['lean_status'] = 'Synthetic fixture; no verified Lean artifact supplied.'
                build.validate_catalog(data, self.root)
            for value in ['', '  \n\t', None, 1, [], {'status': 'checked'}]:
                with self.subTest(collection=collection, invalid_status=value):
                    data = factory()
                    data[collection][0]['lean_status'] = value
                    with self.assertRaises(ValueError):
                        build.validate_catalog(data, self.root)

    def test_authorized_preprint_with_disclosed_attribution_is_valid(self):
        for authors in [[], ['Synthetic Fixture Author']]:
            with self.subTest(authors=authors):
                data = self.with_preprint()
                data['preprints'][0]['authors'] = authors
                data['problems'][0]['status'] = 'proposed_solution_published'
                build.validate_catalog(data, self.root)

    def test_preprint_requires_release_authorization_before_publication(self):
        for field in ['release_approved_by', 'release_approved_at']:
            for form in ['missing', 'empty']:
                with self.subTest(field=field, form=form):
                    data = self.with_preprint()
                    if form == 'missing':
                        del data['preprints'][0][field]
                    else:
                        data['preprints'][0][field] = ''
                    with self.assertRaises(ValueError):
                        build.validate_catalog(data, self.root)
        data = self.with_preprint()
        data['preprints'][0]['release_approved_at'] = '2026-11-07'
        with self.assertRaises(ValueError):
            build.validate_catalog(data, self.root)

    def test_preprint_cannot_mark_a_problem_solved(self):
        data = self.with_preprint()
        data['problems'][0]['status'] = 'project_solution_published'
        with self.assertRaises(ValueError):
            build.validate_catalog(data, self.root)

    def test_preprint_cannot_claim_reviewed_acceptance(self):
        data = self.with_preprint()
        data['preprints'][0]['status'] = 'reviewed'
        with self.assertRaises(ValueError):
            build.validate_catalog(data, self.root)
        for field, value in [('reviewed_by', ['Synthetic Fixture Reviewer']),
                             ('reviewed_at', '2026-11-06')]:
            with self.subTest(field=field):
                data = self.with_preprint()
                data['preprints'][0][field] = value
                with self.assertRaises(ValueError):
                    build.validate_catalog(data, self.root)

    def test_preprint_requires_explicit_attribution_and_known_fields(self):
        for field in ['authors', 'attribution_note']:
            with self.subTest(field=field, form='missing'):
                data = self.with_preprint()
                del data['preprints'][0][field]
                with self.assertRaises(ValueError):
                    build.validate_catalog(data, self.root)
        for field, value in [('authors', ''), ('authors', ['']),
                             ('attribution_note', ''), ('attribution_note', '  ')]:
            with self.subTest(field=field, value=value):
                data = self.with_preprint()
                data['preprints'][0][field] = value
                with self.assertRaises(ValueError):
                    build.validate_catalog(data, self.root)
        data = self.with_preprint()
        data['preprints'][0]['private_notes'] = 'Synthetic unreleased context.'
        with self.assertRaises(ValueError):
            build.validate_catalog(data, self.root)

    def test_preprint_requires_present_safe_public_artifacts(self):
        for field in ['proof_file', 'source_file', 'review_file']:
            for form in ['missing', 'empty', 'nonexistent', 'unsafe']:
                with self.subTest(field=field, form=form):
                    data = self.with_preprint()
                    if form == 'missing':
                        del data['preprints'][0][field]
                    else:
                        data['preprints'][0][field] = {
                            'empty': '',
                            'nonexistent': 'files/missing-artifact.md',
                            'unsafe': 'files/../outside.md',
                        }[form]
                    with self.assertRaises(ValueError):
                        build.validate_catalog(data, self.root)

    def test_unreviewed_candidate_cannot_enter_public_catalogue(self):
        for status in ['candidate_proof', 'conjecture', 'unreviewed', 'solved']:
            with self.subTest(status=status):
                data = self.with_solution()
                data['solutions'][0]['status'] = status
                with self.assertRaises(ValueError):
                    build.validate_catalog(data, self.root)

    def test_missing_review_or_release_authorization_is_rejected(self):
        fields = ['reviewed_by', 'reviewed_at', 'review_file', 'review_summary',
                  'release_approved_by', 'release_approved_at']
        for field in fields:
            with self.subTest(field=field, form='missing'):
                data = self.with_solution()
                del data['solutions'][0][field]
                with self.assertRaises(ValueError):
                    build.validate_catalog(data, self.root)
            with self.subTest(field=field, form='empty'):
                data = self.with_solution()
                data['solutions'][0][field] = [] if field == 'reviewed_by' else ''
                with self.assertRaises(ValueError):
                    build.validate_catalog(data, self.root)

    def test_review_and_authorization_must_precede_release(self):
        for field in ['reviewed_at', 'release_approved_at']:
            with self.subTest(field=field):
                data = self.with_solution()
                data['solutions'][0][field] = '2026-11-07'
                with self.assertRaises(ValueError):
                    build.validate_catalog(data, self.root)

    def test_traversal_hidden_and_executable_artifacts_are_rejected(self):
        (self.root / 'content/outside.md').write_text('Synthetic unreleased text.', encoding='utf-8')
        (self.root / 'outside.md').write_text('Synthetic unreleased text.', encoding='utf-8')
        (self.root / 'content/files/.unreleased.md').write_text('Synthetic unreleased text.', encoding='utf-8')
        (self.root / 'content/files/payload.html').write_text('<p>Synthetic fixture</p>', encoding='utf-8')
        unsafe = ['files/../outside.md', 'files/../../outside.md',
                  str(self.proof), 'files/.unreleased.md', 'files/payload.html']
        for path in unsafe:
            with self.subTest(path=path):
                data = self.with_solution()
                data['solutions'][0]['proof_file'] = path
                with self.assertRaises(ValueError):
                    build.validate_catalog(data, self.root)

    def test_symlink_artifact_is_not_followed(self):
        link = self.root / 'content/files/linked-proof.md'
        try:
            link.symlink_to(self.proof)
        except (OSError, NotImplementedError):
            self.skipTest('Symlinks are unavailable in this execution environment')
        data = self.with_solution()
        data['solutions'][0]['proof_file'] = 'files/linked-proof.md'
        with self.assertRaises(ValueError):
            build.validate_catalog(data, self.root)

    def test_unknown_problem_fields_cannot_leak_into_public_json(self):
        data = copy.deepcopy(self.catalogue)
        data['problems'][0]['private_notes'] = 'Synthetic unreleased note.'
        with self.assertRaises(ValueError):
            build.validate_catalog(data, self.root)

    def test_partial_or_withdrawn_result_cannot_mark_problem_solved(self):
        for scope, status in [('partial_result', 'reviewed'), ('full_solution', 'withdrawn')]:
            with self.subTest(scope=scope, status=status):
                data = self.with_solution()
                data['problems'][0]['status'] = 'project_solution_published'
                data['solutions'][0]['scope'] = scope
                data['solutions'][0]['status'] = status
                if status == 'withdrawn':
                    data['solutions'][0]['withdrawal_reason'] = 'Synthetic withdrawal fixture.'
                with self.assertRaises(ValueError):
                    build.validate_catalog(data, self.root)

    def test_build_copies_only_explicit_publication_files_and_removes_stale_output(self):
        data = self.with_solution()
        source = self.root / 'content/files/fixture-source-v1.tex'
        source.write_text('% Synthetic fixture only.\n', encoding='utf-8')
        data['solutions'][0]['source_file'] = 'files/fixture-source-v1.tex'
        unreferenced = self.root / 'content/files/unreleased-draft.txt'
        unreferenced.write_text('SYNTHETIC UNRELEASED MATERIAL — not for deployment.', encoding='utf-8')
        (self.root / 'content/catalog.json').write_text(json.dumps(data), encoding='utf-8')
        (self.root / 'assets/site.css').write_text('/* Synthetic asset */', encoding='utf-8')
        (self.root / 'dist').mkdir()
        (self.root / 'dist/stale-unreleased.txt').write_text('Synthetic stale output.', encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()):
            build.build(self.root)
        self.assertEqual((self.root / 'dist/files/fixture-proof-v1.md').read_bytes(), self.proof.read_bytes())
        self.assertEqual((self.root / 'dist/files/fixture-review-v1.txt').read_bytes(), self.review.read_bytes())
        self.assertEqual((self.root / 'dist/files/fixture-source-v1.tex').read_bytes(), source.read_bytes())
        self.assertTrue((self.root / 'dist/publications/synthetic-fixture-v1/index.html').is_file())
        self.assertFalse((self.root / 'dist/files/unreleased-draft.txt').exists())
        self.assertFalse((self.root / 'dist/stale-unreleased.txt').exists())
        self.assertFalse((self.root / 'dist/content').exists())
        for path in (self.root / 'dist').rglob('*'):
            if path.is_file():
                self.assertNotIn(b'SYNTHETIC UNRELEASED MATERIAL', path.read_bytes())


if __name__ == '__main__':
    unittest.main()
