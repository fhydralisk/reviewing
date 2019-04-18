from unittest import TestCase
from .. import field_choice


class TestFieldChoice2(TestCase):
    def create_good_field_choice(self):
        class FieldChoiceGood(field_choice.FieldChoice2):
            t1 = field_choice.FieldChoiceSelection(1, 'test1', alias='t1_alias')
            t2 = field_choice.FieldChoiceSelection(2, 'test2')
            t3 = field_choice.FieldChoiceSelection(3, 'test3', alias='t3')
            t4s = field_choice.FieldChoiceSelection('4', alias='t4')
            t5 = field_choice.FieldChoiceSelection(5, 'test5', alias='t5')
            t6 = field_choice.FieldChoiceSelection(6, 'test6', alias='t6')
            t7 = field_choice.FieldChoiceSelection(7, 'test7', alias='t7')
            ts1 = field_choice.Fieldset(['t1', t2, t4s], alias='ts1_alias')
            ts2 = field_choice.Fieldset(['ts1', t3], "testset2")
            ts3 = field_choice.Fieldset([ts1, ts2])
            ts4 = field_choice.Fieldset("ts3")

        return FieldChoiceGood()

    def create_bad_dup(self):
        class FieldChoiceBad(field_choice.FieldChoice2):
            t1 = field_choice.FieldChoiceSelection(1)
            t2 = field_choice.FieldChoiceSelection(1)

        return FieldChoiceBad()

    def create_bad_dup_alias(self):
        class FieldChoiceBad(field_choice.FieldChoice2):
            t1 = field_choice.FieldChoiceSelection(1, alias='t1')
            t2 = field_choice.FieldChoiceSelection(2, alias='t1')

        return FieldChoiceBad()

    def create_bad_cycle(self):
        class FieldChoiceBad(field_choice.FieldChoice2):
            t1 = field_choice.FieldChoiceSelection(1)
            t2 = field_choice.FieldChoiceSelection(2)
            ts1 = field_choice.Fieldset([t1, 'ts2'])
            ts2 = field_choice.Fieldset([t2, 'ts1'])

        return FieldChoiceBad()

    def test_has_field_set(self):
        container = field_choice.FieldsetContainer(None, [1, 3, 5])
        self.assertEqual(container.__hash__(), (1, 3, 5).__hash__())

    def test_check_dup(self):
        self.assertRaises(ValueError, self.create_bad_dup)
        self.assertRaises(ValueError, self.create_bad_dup_alias)

    def test_check_recycle(self):
        self.assertRaises(RuntimeError, self.create_bad_cycle)

    def test_good_choice(self):
        choice = self.create_good_field_choice()
        ts1_data = {1, 2, '4'}
        ts2_ts4_data = {1, 2, 3, '4'}
        # basic tests
        self.assertEqual(choice.t1, 1)
        self.assertEqual(choice.t4s, '4')
        self.assertNotEqual(choice.t4s, 4)
        self.assertSetEqual(choice.ts1, ts1_data)
        self.assertSetEqual(choice.ts2, ts2_ts4_data)
        self.assertSetEqual(choice.ts4, ts2_ts4_data)

        # test alias choices
        self.assertSetEqual(set(choice.alias_choice.get_choices()), {'t1_alias', 't2', 't3', 't4', 't5', 't6', 't7'})
        self.assertSetEqual(
            set(choice.alias_choice.get_choices()),
            {'t1_alias', 't2', 't3', 't4', 't5', 't6', 't7'}
        )  # test cache
        self.assertSetEqual(set(choice.ts1.sub_choice.get_choices()), ts1_data)

        # test verbose name
        self.assertEqual(choice.get_verbose_name(1), 'test1')
        self.assertEqual(choice.get_verbose_name('t4s', use_field_name=True), 't4s')

        # test alias
        self.assertEqual(choice.get_alias_real_data('t1_alias'), 1)
        self.assertSetEqual(choice.get_alias_real_data('ts1_alias'), ts1_data)
        self.assertSetEqual(choice.get_alias_real_data('ts2'), ts2_ts4_data)
        self.assertEqual(choice.get_alias(1), 't1_alias')
        self.assertEqual(choice.get_alias('t4s', use_field_name=True), 't4')
        self.assertEqual(choice.get_alias('ts1', use_field_name=True), 'ts1_alias')
        self.assertRaises(KeyError, choice.get_alias, 8)
        self.assertRaises(KeyError, choice.get_alias, 't5s', use_field_name=True)

        # test set choice
        self.assertRaises(ValueError, choice.get_set_choice)
        set_choice = choice.get_set_choice(fields=['ts1', 'ts2'])
        self.assertSetEqual(set(set_choice._fields.keys()), {'ts1', 'ts2'})
        self.assertSetEqual(set_choice.ts1, ts1_data)
        self.assertSetEqual(set(set_choice.alias_choice.get_choices()), {'ts1_alias', 'ts2'})
        self.assertSetEqual(set_choice.get_alias_real_data('ts1_alias'), ts1_data)
