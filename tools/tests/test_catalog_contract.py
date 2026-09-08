import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_catalog import build_entry
from skill_utils import validate_skill_tree
from validate_marketplace import validate

ROOT = Path(__file__).resolve().parents[2]


class CatalogContractTest(unittest.TestCase):
    def test_no_membership_does_not_invent_plugin_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'example'
            root.mkdir()
            (root / 'SKILL.md').write_text('---\nname: example\ndescription: Use when asked.\nmetadata:\n  summary: Produce a useful result.\n---\n# Example\n')
            entry = build_entry(root, {})
            self.assertEqual(entry['install']['claude_plugin'], [])
            self.assertEqual(entry['summary'], 'Produce a useful result.')
            entry = build_entry(root, {'example': ['precon']})
            self.assertEqual(entry['install']['claude_plugin'][-1], '/plugin install precon@buildr')

    def test_missing_and_non_markdown_samples(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'rfp-intake'
            shutil.copytree(ROOT / 'skills/rfp-intake', root)
            shutil.rmtree(root / 'samples')
            errors = validate_skill_tree(root)
            self.assertTrue(any('samples/input-' in e for e in errors))
            self.assertTrue(any('samples/output-' in e for e in errors))
            (root / 'samples').mkdir()
            (root / 'samples/input-case.json').write_text('{}')
            (root / 'samples/output-case.csv').write_text('value\n1\n')
            self.assertFalse(any('missing synthetic sample' in e for e in validate_skill_tree(root)))

    def test_summary_required_and_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'rfp-intake'
            shutil.copytree(ROOT / 'skills/rfp-intake', root)
            path = root / 'SKILL.md'
            from skill_utils import split_frontmatter
            import yaml
            metadata, body = split_frontmatter(path.read_text())
            metadata['metadata'].pop('summary', None)
            path.write_text('---\n' + yaml.safe_dump(metadata) + '---\n' + body)
            self.assertIn('metadata.summary must be a non-empty string', validate_skill_tree(root))
            metadata['metadata']['summary'] = 'x' * 201
            path.write_text('---\n' + yaml.safe_dump(metadata) + '---\n' + body)
            self.assertIn('metadata.summary exceeds 200 characters', validate_skill_tree(root))

    def test_manifest_coverage_duplicates_and_unknown_paths(self):
        good = {'plugins': [{'name': 'all', 'skills': ['./skills/one']}]}
        self.assertEqual(validate(good, {'one'}), [])
        self.assertTrue(validate(good, {'one', 'two'}))
        bad = {'plugins': [{'name': 'all', 'skills': ['./skills/one', './skills/one', '../other']}]}
        errors = validate(bad, {'one'})
        self.assertTrue(any('duplicate' in e for e in errors))
        self.assertTrue(any('unknown' in e for e in errors))
        for name in ('', [], None):
            self.assertTrue(validate({'plugins': [{'name': name, 'skills': []}]}, {'one'}))


if __name__ == '__main__':
    unittest.main()
