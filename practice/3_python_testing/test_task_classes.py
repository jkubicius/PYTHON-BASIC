"""
Write tests for classes in 2_python_part_2/task_classes.py (Homework, Teacher, Student).
Check if all methods working correctly.
Also check corner-cases, for example if homework number of days is negative.
"""
import io
import importlib
import datetime
import unittest
from unittest.mock import patch

res = importlib.import_module('practice.2_python_part_2.task_classes')


class TestClasses(unittest.TestCase):
    def setUp(self): # creating teacher and student objects before each test
        self.teacher = res.Teacher('Dmitry', 'Orlyakov')
        self.student = res.Student('Vladislav', 'Popov')

        self.expired_homework = self.teacher.create_homework('Learn functions', 0)
        self.oop_homework = self.teacher.create_homework('create 2 simple classes', 5)

    def test_teacher_names(self):
        self.assertEqual(self.teacher.last_name, 'Orlyakov')
        self.assertEqual(self.teacher.first_name, 'Dmitry')

    def test_student_names(self):
        self.assertEqual(self.student.last_name, 'Popov')
        self.assertEqual(self.student.first_name, 'Vladislav')

    def test_expired_homework_properties(self):
        self.assertIsInstance(self.expired_homework.created, datetime.datetime)
        self.assertEqual(self.expired_homework.deadline, datetime.timedelta(0))
        self.assertEqual(self.expired_homework.text, 'Learn functions')

    def test_active_homework_properties(self):
        self.assertIsInstance(self.oop_homework.created, datetime.datetime)
        self.assertEqual(self.oop_homework.deadline, datetime.timedelta(5))
        self.assertEqual(self.oop_homework.text, 'create 2 simple classes')

    def test_homework_is_active(self):
        self.assertFalse(self.expired_homework.is_active())
        self.assertTrue(self.oop_homework.is_active())

    def test_student_does_active_homework(self):
        result = self.student.do_homework(self.oop_homework)
        self.assertIsInstance(result, res.Homework)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_student_does_expired_homework(self, mock_stdout):
        result = self.student.do_homework(self.expired_homework)
        self.assertIsNone(result)
        self.assertEqual(mock_stdout.getvalue(), 'You are late\n')


if __name__ == '__main__':
    unittest.main()
