from django.test import TestCase

from authlib.utils import positional


@positional(1)
def test(*args):
    return args


class Test(TestCase):
    def test_positional(self):
        self.assertEqual(test(1), (1,))
        with self.assertRaises(TypeError):
            test(1, 2)
