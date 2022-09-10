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
			self.head.next = new_head
			self.head = new_head
	
	def push_back(self, data):
		if self.tail is None:
			self.tail = Node(data, None, None)
			self.head = self.tail
		else:
			new_tail = Node(data, None, self.tail)
			self.tail.prev = new_tail
			self.tail = new_tail
	
	def front(self):
		if self.head is None:
			return None
		else:
			return self.head.data
	
	def back(self):
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
			else:
				self.tail = None
			self.head = new_head
	
	def pop_back(self):
		if self.tail is None:
			return
		else:
			new_tail = self.tail.next
			if new_tail is not None:
				new_tail.prev = None
			else:
				self.head = None
			self.tail = new_tail

def vector_field():
	# 1D arrays
	x = np.arange(-5,5,0.1)
	y = np.arange(-5,5,0.1)
	
	# Meshgrid
	X,Y = np.meshgrid(x,y)
	
	# Assign vector directions
	Ex = (X + 1)/((X+1)**2 + Y**2) - (X - 1)/((X-1)**2 + Y**2)
	Ey = Y/((X+1)**2 + Y**2) - Y/((X-1)**2 + Y**2)
	
	return (X,Y,Ex,Ey)

def generate_stream_lines(X,Y,Ex,Ey):
	# Depict illustration
	plt.figure(figsize=(10, 10))
	streamlines = plt.streamplot(X, Y, Ex, Ey, density=1.4, linewidth=None, color='#A23BEC')
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
	
	stream_lines = []
	for segment_key in segments_start:
		stream_line = []
		segment = segments_start[segment_key]
		while not segment.empty():
			point = segment.front()
			stream_line.append(point)
			segment.pop_front()
		stream_lines.append(stream_line)
	
	return stream_lines

def cumulative_distance(line):
	cumulative_length = 0.0
	lengths = []
	previous_point = None
	
	for point in line:
		if previous_point is None:
			distance = 0.0
		else:
			distance = np.linalg.norm(point - previous_point)
		
		cumulative_length = cumulative_length + distance
		lengths.append(cumulative_length)
		previous_point = point
	
	return lengths

def find_midpoint(line):
	if len(line) < 2:
		return None
	
	lengths = cumulative_distance(line)
	total_length = lengths[-1]
	
	mid_length = 0.5 * total_length
	
	for n in range(0, len(line)-1):
		if lengths[n+1] > mid_length:
			distance = lengths[n+1] - lengths[n]
			difference = lengths[n+1] - mid_length
			
			location_fraction = difference/distance
			if location_fraction < 0.01:
				loction_fraction = 0.01
			
			end_point_fraction = location_fraction
			if end_point_fraction > 0.5:
				end_point_fraction = 1 - end_point_fraction
			
			displacement = line[n+1] - line[n]
			
			mid_segment = line[n] + location_fraction * displacement
			initial_point = mid_segment - end_point_fraction * displacement
			final_point = mid_segment + end_point_fraction * displacement
			
			return (initial_point, mid_segment, final_point)
	
	return None

def write_stream_lines(filename, stream_lines):
	with open(filename, "w") as file:
		separate_next_line = False
		for line in stream_lines:
			if not separate_next_line:
				separate_next_line = True
			else:
				file.write("\n")
			for point in line:
				file.write(f"{point[0]:.16f}")
				file.write("; ")
				file.write(f"{point[1]:.16f}")
				file.write("\n")

def write_stream_arrows(filename, arrows):
	with open(filename, "w") as file:
		separate_next_line = False
		for arrow in arrows:
			if not separate_next_line:
				separate_next_line = True
			else:
				file.write("\n")
				
			p0, p1, p2 = arrow
			file.write(f"{p0[0]:.16f}")
			file.write("; ")
			file.write(f"{p0[1]:.16f}")
			file.write("; ")
			file.write(f"{p1[0]:.16f}")
			file.write("; ")
			file.write(f"{p1[1]:.16f}")
			file.write("; ")
			file.write(f"{p2[0]:.16f}")
			file.write("; ")
			file.write(f"{p2[1]:.16f}")
			file.write("\n")

def test():
	(X,Y,Ex,Ey) = vector_field()
	stream_lines = generate_stream_lines(X,Y,Ex,Ey)
	write_stream_lines("streamlines.dat", stream_lines)
	stream_arrows = list(map(find_midpoint, stream_lines))
	return stream_arrows

def main():
	(X,Y,Ex,Ey) = vector_field()
	stream_lines = generate_stream_lines(X,Y,Ex,Ey)
	write_stream_lines("streamlines.dat", stream_lines)
	stream_arrows = list(map(find_midpoint, stream_lines))
	write_stream_arrows("stream_arrows.dat", stream_arrows)

if __name__ == '__main__':
	main()
