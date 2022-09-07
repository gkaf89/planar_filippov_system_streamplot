# Import required modules
import numpy as np
import matplotlib.pyplot as plt
import bitstring as btstr

class Node:
	def __init__(self, data, prev, next):
		self.data = data
		self.prev = prev
		self.next = next
	
	@classmethod
	def empty():
		return Node(None, None, None)
	
	@classmethod
	def create(data, prev, next):
		return Node(data, prev, next)


class DoublyLinkedList:
	def __init__(self):
		self.head = None
		self.tail = None
	
	def empty(self):
		return (self.head is None) and (self.tail is None)
		
	def push_front(self, data):
		if self.head is None:
			self.head = Node(data, None, None)
			self.tail = self.head
		else:
			new_head = Node(data, self.head, None)
			self.head = new_head
	
	def push_back(self, data):
		if self.tail is None:
			self.tail = Node(data, None, None)
			self.head = self.tail
		else:
			new_tail = Node(data, None, self.tail)
			self.tail = new_tail
	
	def get_front(self):
		if self.head is None:
			return None
		else:
			return self.head.data
	
	def get_back(self):
		if self.tail is None:
			return None
		else:
			return self.tail.data 
	
	def pop_front(self):
		if self.head is None:
			return
		else:
			new_head = self.head.prev
			if new_head is not None:
				new_head.next = None
			self.head = new_head
	
	def pop_back(self):
		if self.tail is None:
			return
		else:
			new_tail = self.tail.next
			if new_tail is not None:
				new_tail.prev = None
			self.tail = new_tail

# xs1 = bitstring.BitArray(float=asd[1][0,1], length=64).bin

def main():
	# 1D arrays
	x = np.arange(-5,5,0.1)
	y = np.arange(-5,5,0.1)
	
	# Meshgrid
	X,Y = np.meshgrid(x,y)
	
	# Assign vector directions
	Ex = (X + 1)/((X+1)**2 + Y**2) - (X - 1)/((X-1)**2 + Y**2)
	Ey = Y/((X+1)**2 + Y**2) - Y/((X-1)**2 + Y**2)
	
	# Depict illustration
	plt.figure(figsize=(10, 10))
	streamlines = plt.streamplot(X,Y,Ex,Ey, density=1.4, linewidth=None, color='#A23BEC')
	line_segments = streamlines.lines.get_segments()
	
	segments_start = {}
	segments_end = {}
	for segment in line_segments:
		start_point = segment[0,:]
		c0 = btstr.BitArray(float=start_point[0], length=64).hex
		c1 = btstr.BitArray(float=start_point[1], length=64).hex
		key_point_start = (c0, c1)
		
		end_point = segment[1,:]
		c0 = btstr.BitArray(float=end_point[0], length=64).hex
		c1 = btstr.BitArray(float=end_point[1], length=64).hex
		key_point_end = (c0, c1)
		
		segment_positioned = False
		if key_point_start in segments_end:
			extendable_segment = segments_end.pop(key_point_start)
			extendable_segment.push_front(start_point)
			segments_end[key_point_end] = extendable_segment
			segment_positioned = True
		if key_point_end in segments_start:
			extendable_segment = segments_start.pop(key_point_end)
			extendable_segment.push_back(segment)
			segments_start[key_point_start] = extendable_segment
			segment_positioned = True
		
		if not segment_positioned:
			extendable_segment = DoublyLinkedList()
			extendable_segment.push_front(end_point)
			extendable_segment.push_back(start_point)
			segments_end[key_point_end] = extendable_segment
			segments_start[key_point_start] = extendable_segment
	print(len(segments_end))
	print(len(segments_start))

if __name__ == '__main__':
	main()
