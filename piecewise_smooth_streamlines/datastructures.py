class _Node:
	def __init__(self, data, prev, next):
		self.data = data
		self.prev = prev
		self.next = next
	
	@staticmethod
	def empty():
		return _Node(None, None, None)
	
	@staticmethod
	def create(data, prev, next):
		return _Node(data, prev, next)

class Dequeue:
	def __init__(self):
		self.__head = None
		self.__tail = None
	
	def empty(self):
		return (self.__head is None) and (self.__tail is None)
	
	def size(self):
		current = self.__head
		n = 0
		while current is not None:
			n = n + 1
			current = current.prev
		
		return n
	
	def push_front(self, data):
		if self.__head is None:
			self.__head = _Node(data, None, None)
			self.__tail = self.__head
		else:
			new_head = _Node(data, self.__head, None)
			self.__head.next = new_head
			self.__head = new_head
	
	def push_back(self, data):
		if self.__tail is None:
			self.__tail = _Node(data, None, None)
			self.__head = self.__tail
		else:
			new_tail = _Node(data, None, self.__tail)
			self.__tail.prev = new_tail
			self.__tail = new_tail
	
	def front(self):
		if self.__head is None:
			return None
		else:
			return self.__head.data
	
	def back(self):
		if self.__tail is None:
			return None
		else:
			return self.__tail.data
	
	def pop_front(self):
		if self.__head is None:
			return
		else:
			new_head = self.__head.prev
			if new_head is not None:
				new_head.next = None
			else:
				self.__tail = None
			self.__head = new_head
	
	def pop_back(self):
		if self.__tail is None:
			return
		else:
			new_tail = self.__tail.next
			if new_tail is not None:
				new_tail.prev = None
			else:
				self.__head = None
			self.__tail = new_tail
	
	def append_front(self, other):
		self.__head.next = other.__tail
		other.__tail.prev = self.__head
		
		self.__head = other.__head
	
	def append_back(self, other):
		self.__tail.prev = other.__head
		other.__head.next = self.__tail
		
		self.__tail = other.__tail
	
	def to_list(self):
		ls= []
		while not(self.empty()):
			ls.append(self.back())
			self.pop_back()
		return ls

def main():
	test_results = []
	
	dequeue = Dequeue()
	
	test_results.append(dequeue.empty())
	
	dequeue.push_front(1)
	test_results.append(dequeue.front() == 1 and dequeue.back() == 1)
	
	dequeue.pop_front()
	test_results.append(dequeue.empty())
	
	dequeue.push_front(1)
	test_results.append(dequeue.front() == 1 and dequeue.back() == 1)
	
	dequeue.pop_back()
	test_results.append(dequeue.empty())
	
	dequeue.push_front(1)
	dequeue.push_back(2)
	test_results.append(dequeue.front() == 1 and dequeue.back() == 2)

if __name__ == '__main__':
	import unittest
	main()
