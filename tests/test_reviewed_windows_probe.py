"""Independent Windows probe of the exact v0.13.1 reviewed upgrade code."""
import base64
import hashlib
import json
import os
from pathlib import Path
import unittest

from tests import test_upgrade_windows as support


@unittest.skipUnless(os.name == 'nt', 'native Windows fixture')
class ReviewedWindowsProbe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        support.WindowsUpgradeTests.setUpClass.__func__(cls)

    setUp = support.WindowsUpgradeTests.setUp
    cli = support.WindowsUpgradeTests.cli
    plan = support.WindowsUpgradeTests.plan
    powershell = support.WindowsUpgradeTests.powershell

    def test_reviewed_core_adoption_guard_retention_and_rollback(self):
        agents = self.target / 'AGENTS.md'
        local = agents.read_bytes().replace('AI 协作协议'.encode(), 'Blog AI 协作协议'.encode(), 1)
        agents.write_bytes(local + b'Blog exterior rule.\r\n')
        source_agents = self.source / 'core/AGENTS.md'
        source_agents.write_bytes(source_agents.read_bytes().replace(
            'AI 协作协议'.encode(), 'Distribution AI 协作协议'.encode(), 1))
        adoption = self.target / 'docs/WORKFLOW-ADOPTION.md'
        adoption.write_bytes(adoption.read_bytes().replace(b'updated: YYYY-MM-DD', b'updated: 2026-01-01', 1))
        source_adoption = self.source / 'core/docs/WORKFLOW-ADOPTION.md'
        source_adoption.write_bytes(source_adoption.read_bytes().replace(
            b'updated: YYYY-MM-DD', b'updated: 2026-02-01', 1))
        guard = self.target / 'scripts/delivery_guard.py'
        guard.write_bytes(guard.read_bytes() + b'\n# Blog permission rule.\n')
        source_guard = self.source / 'core/scripts/delivery_guard.py'
        source_guard.write_bytes(source_guard.read_bytes() + b'\n# Distribution guard change.\n')
        before = support.snapshot(self.target)
        plan = self.plan()
        self.assertEqual(set(plan['conflicts']), {'AGENTS.md', 'docs/WORKFLOW-ADOPTION.md',
                                                   'scripts/delivery_guard.py'})
        rows = {row['path']: row for row in plan['entries']}
        def choice(name, decision, payload=None):
            row = rows[name]
            entry = {key: row[key] for key in ('path', 'beforeSha256', 'baselineSha256',
                                              'nextBaselineSha256')}
            entry['decision'] = decision
            if payload is None:
                entry['resultSha256'] = hashlib.sha256((self.target / name).read_bytes()).hexdigest()
            else:
                entry['resultBase64'] = base64.b64encode(payload).decode('ascii')
            return entry
        first = agents.read_bytes()
        incoming = source_agents.read_bytes()
        start = support.CORE_START
        end = support.CORE_END
        a, b = first.index(start), first.index(end) + len(end) + 2
        c, d = incoming.index(start), incoming.index(end) + len(end) + 2
        reviewed = first[:a] + incoming[c:d] + first[b:]
        spec = {'schemaVersion': 1, 'kind': 'workflow-upgrade-resolution', 'entries': [
            choice('AGENTS.md', 'replace-core-block', reviewed),
            choice('docs/WORKFLOW-ADOPTION.md', 'replace-file', adoption.read_bytes() + b'\nReviewed.\n'),
            choice('scripts/delivery_guard.py', 'retain')]}
        resolution = self.root / 'resolution.json'
        resolution.write_text(json.dumps(spec))
        resolved = self.root / 'resolved.json'
        outcome = self.cli('resolve-plan', '--target', self.target, '--plan', self.plan_path,
                           '--resolution', resolution, '--output', resolved)
        self.assertEqual(outcome.returncode, 0, outcome.stdout + outcome.stderr)
        outcome = self.cli('apply-resolved', '--target', self.target, '--plan', resolved)
        self.assertEqual(outcome.returncode, 0, outcome.stdout + outcome.stderr)
        transaction = json.loads(outcome.stdout)['transaction']
        self.assertEqual(guard.read_bytes(), before['scripts/delivery_guard.py'])
        strict = self.cli('check', '--target', self.target, '--strict', '--json')
        self.assertEqual(strict.returncode, 0, strict.stdout + strict.stderr)
        audit = self.powershell('audit')
        self.assertEqual(audit.returncode, 2, audit.stdout + audit.stderr)
        self.assertIn('reviewed', (audit.stdout + audit.stderr).lower())
        outcome = self.cli('rollback', '--target', self.target, '--transaction', transaction)
        self.assertEqual(outcome.returncode, 0, outcome.stdout + outcome.stderr)
        for name, data in before.items():
            self.assertEqual((self.target / name).read_bytes(), data, name)


if __name__ == '__main__':
    unittest.main()
