'tests for should/config.py'
from unittest import TestCase

from should.config import merge_configs

class MergeConfigsTestCase(TestCase):
    'test merge_configs'
    def test_merge_basic_dicts(self):
        'merge_configs overwrites basic dicts'
        self.assertEqual(
            {'a': 2},
            merge_configs(
                {'a': 1},
                {'a': 2},
            )
        )

    def test_add(self):
        'merge_configs add scalar values'
        self.assertEqual(
            {'a': 1},
            merge_configs(
                {},
                {'a': 1},
            )
        )

    def test_add_special(self):
        'merge_configs adds special values'
        self.assertEqual(
            {'a': [1]},
            merge_configs(
                {},
                {'a': [1]},
            )
        )

    def test_merge_lists(self):
        'merge_configs adds lists'
        self.assertEqual(
            {'a': [1, 2]},
            merge_configs(
                {'a': [1]},
                {'a': [2]},
            )
        )

    def test_merge_1_dict(self):
        'merge_configs merges 1-deep dicts'
        self.assertEqual(
            {'a': {'a': 1, 'b': 2}},
            merge_configs(
                {'a': {'a': 1}},
                {'a': {'b': 2}},
            )
        )

    def test_merge_2_dict(self):
        'merge_configs merges 2-deep dicts'
        self.assertEqual(
            {'a': {'a': {'a': 1, 'b': 2}}},
            merge_configs(
                {'a': {'a': {'a': 1}}},
                {'a': {'a': {'b': 2}}},
            )
        )
