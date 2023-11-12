from datastructures import Dequeue
import unittest

class TestEmpty(unittest.TestCase):
	def test_empty(self) -> None:
		dq : Dequeue[int] = Dequeue()
		self.assertTrue(dq.empty())

class TestInsertion(unittest.TestCase):
	def __init__(self, *args, **kwargs) -> None:
		super(TestInsertion, self).__init__(*args, **kwargs)
		self.dequeue : Dequeue[int] = Dequeue()
		self.dequeue.push_front(0)
	
	def test_front(self) -> None:
		self.assertEqual(self.dequeue.front(), 0)
	
	def test_bask(self) -> None:
		self.assertEqual(self.dequeue.back(), 0)

class TestInsertionReuseAfterEmpty(unittest.TestCase):
	def __init__(self, *args, **kwargs) -> None:
		super(TestInsertionReuseAfterEmpty, self).__init__(*args, **kwargs)
		self.dequeue : Dequeue[int] = Dequeue()
		self.dequeue.push_front(0)
		self.dequeue.pop_front()
		self.dequeue.push_front(1)
	
	def test_front(self) -> None:
		self.assertEqual(self.dequeue.front(), 1)
	
	def test_back(self) -> None:
		self.assertEqual(self.dequeue.back(), 1)

class TestInsertionEptyingTwice(unittest.TestCase):
	def test_empty(self) -> None:
		dequeue : Dequeue[int] = Dequeue()
		dequeue.push_front(0)
		dequeue.pop_front()
		self.assertTrue(dequeue.empty())
		dequeue.push_front(1)
		dequeue.pop_front()
		self.assertTrue(dequeue.empty())

class TestInsertionEmptyingTwiceTwoSided(unittest.TestCase):
	def test_empty(self) -> None:
		dequeue : Dequeue[int] = Dequeue()
		dequeue.push_front(0)
		dequeue.pop_front()
		self.assertTrue(dequeue.empty())
		dequeue.push_front(1)
		dequeue.pop_back()
		self.assertTrue(dequeue.empty())

class TestInsertionTwice(unittest.TestCase):
	def __init__(self, *args, **kwargs) -> None:
		super(TestInsertionTwice, self).__init__(*args, **kwargs)
		self.dequeue : Dequeue[int] = Dequeue()
		self.dequeue.push_front(0)
		self.dequeue.push_back(1)
	
	def test_front(self) -> None:
		self.assertEqual(self.dequeue.front(), 0)
	
	def test_bask(self) -> None:
		self.assertEqual(self.dequeue.back(), 1)

def main() -> None:
	unittest.main()

if __name__ == '__main__':
	main()
