import numpy as np
import matplotlib.pyplot as plt
import bitstring as btstr

import sys
import os

import datastructures as struct

class _LineKeys:
	def __init__(self):
		self.__begin = {}
		self.__end = {}
	
	def insert(self, k):
		k_begin, k_end = k
		self.__begin[k_begin] = k
		self.__end[k_end] = k
	
	def pop_front(self, k_end):
		k = self.__begin.pop(k_end)
		self.__end.pop(k[1])
		return k
	
	def pop_back(self, k_begin):
		k = self.__end.pop(k_begin)
		self.__begin.pop(k[0])
		return k
	
	def get_front_keys(self):
		return self.__begin
	
	def get_back_keys(self):
		return self.__end

class _Lines:
	def __init__(self):
		self.__line_keys = _LineKeys()
		self.__begin = {}
		self.__end = {}
	
	def insert(self, k, line):
		self.__line_keys.insert(k)
		
		k_begin, k_end = k
		
		self.__begin[k_begin] = line
		self.__end[k_end] = line
	
	def pop_front(self, k_end):
		k = self.__line_keys.pop_front(k_end)
		line = self.__begin.pop(k[0])
		self.__end.pop(k[1])
		
		return (k, line)
	
	def pop_back(self, k_begin):
		k = self.__line_keys.pop_back(k_begin)
		line = self.__end.pop(k[1])
		self.__begin.pop(k[0])
		
		return (k, line)
	
	def get_front_list(self):
		return (self.__line_keys.get_front_keys(), self.__begin)
	
	def get_back_list(self):
		return (self.__line_keys.get_back_keys(), self.__end)
	
	def exists_line_begining_with(self, key):
		return key in self.__line_keys.get_front_keys()
	
	def exists_line_ending_with(self, key):
		return key in self.__line_keys.get_back_keys()

def phase_plane_grid(vector_field, min_value, max_value, step):
	# 1D arrays
	x = np.arange(min_value[0], max_value[0], step[0])
	y = np.arange(min_value[1], max_value[1], step[1])
	
	# Meshgrid
	X, Y = np.meshgrid(x, y)
	
	# Assign vector directions
	Fx, Fy = vector_field(X, Y)
	
	return (X, Y, Fx, Fy)

def point_to_key(point):
	c0 = btstr.BitArray(float=point[0], length=64).hex
	c1 = btstr.BitArray(float=point[1], length=64).hex
	return (c0, c1)

def segment_to_key(segment):
	k_begin = point_to_key(segment[0,:])
	k_end = point_to_key(segment[1,:])
	
	return (k_begin, k_end)

def process_segment(lines, segment):
	k = segment_to_key(segment)
	k_begin, k_end = k
	
	if lines.exists_line_begining_with(k_end):
		if lines.exists_line_ending_with(k_begin):
			key_back, line_back = lines.pop_front(k_end)
			key_front, line_front = lines.pop_back(k_begin)
			line_front.append_back(line_back)
			lines.insert((key_front[0], key_back[1]), line_front)
		else:
			line_key, line = lines.pop_front(k_end)
			line.push_front(segment[0,:])
			lines.insert((k_begin, line_key[1]), line)
	elif lines.exists_line_ending_with(k_begin):
		line_key, line = lines.pop_back(k_begin)
		line.push_back(segment[1,:])
		lines.insert((line_key[0], k_end), line)
	else:
		line = struct.Dequeue()
		line.push_front(segment[0,:])
		line.push_back(segment[1,:])
		lines.insert(k, line)

def lines_to_list(line_segments):
	keys, lines = line_segments.get_front_list()
	
	stream_lines = []
	for line_key in keys:
		stream_line = []
		line = lines[line_key]
		while not line.empty():
			point = line.front()
			stream_line.append(point)
			line.pop_front()
		stream_lines.append(stream_line)
	
	return stream_lines

def is_singular(segment):
	k_begin, k_end = segment_to_key(segment)
	return k_begin == k_end

def segments_to_streamlines(segments):
	non_singular_segments = filter(lambda segment : not(is_singular(segment)), segments)
	
	lines = _Lines()
	for segment in non_singular_segments:
		process_segment(lines, segment)
	
	stream_lines = lines_to_list(lines)
	
	return stream_lines

def generate_stream_lines(X, Y, Fx, Fy, *argv, **kwargs):
	# Depict illustration
	streamlines = plt.streamplot(X, Y, Fx, Fy, *argv, **kwargs)
	line_segments = streamlines.lines.get_segments()
	
	stream_lines = segments_to_streamlines(line_segments)

	return stream_lines

def __cumulative_distance(line):
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

def __ensure_minimum_edge_separation(location_fraction, min_edge_fraction):
	location_fraction = max( min_edge_fraction, location_fraction )
	location_fraction = min( 1 - min_edge_fraction, location_fraction )
	
	return location_fraction

def __find_midpoint(line, min_edge_fraction = 0.01):
	if len(line) < 2:
		return None
	
	lengths = __cumulative_distance(line)
	total_length = lengths[-1]
	
	mid_length = 0.5 * total_length
	
	for n in range(0, len(line)-1):
		if lengths[n+1] > mid_length:
			distance = lengths[n+1] - lengths[n]
			difference = mid_length - lengths[n]
			
			location_fraction = difference/distance
			location_fraction = __ensure_minimum_edge_separation(location_fraction, min_edge_fraction)
			
			end_point_fraction = min( location_fraction, 1 - location_fraction )
			
			displacement = line[n+1] - line[n]
			
			mid_segment = line[n] + location_fraction * displacement
			initial_point = mid_segment - end_point_fraction * displacement
			final_point = mid_segment + end_point_fraction * displacement
			
			return (initial_point, mid_segment, final_point)
	return None

def generate_stream_arrows(stream_lines):
	return list(map(__find_midpoint, stream_lines))

def write_stream_lines(filename, stream_lines):
	with open(filename, 'w') as file:
		separate_next_line = False
		for line in stream_lines:
			if not separate_next_line:
				separate_next_line = True
			else:
				file.write('\n')
			for point in line:
				file.write(f'{point[0]:.16f}')
				file.write('; ')
				file.write(f'{point[1]:.16f}')
				file.write('\n')

def write_stream_arrows(filename, arrows):
	with open(filename, 'w') as file:
		separate_next_line = False
		for arrow in arrows:
			if not separate_next_line:
				separate_next_line = True
			else:
				file.write('\n')
			
			p0, p1, p2 = arrow
			file.write(f'{p0[0]:.16f}')
			file.write('; ')
			file.write(f'{p0[1]:.16f}')
			file.write('; ')
			file.write(f'{p1[0]:.16f}')
			file.write('; ')
			file.write(f'{p1[1]:.16f}')
			file.write('; ')
			file.write(f'{p2[0]:.16f}')
			file.write('; ')
			file.write(f'{p2[1]:.16f}')

class Streamplot:
	def __init__(self, streamlines, streamarrows):
		self.streamlines = streamlines
		self.streamarrows = streamarrows

def create_streamplot(vector_field, min_value, max_value, step, *argv, **kwargs):
	X,Y,Ex,Ey = phase_plane_grid(vector_field, min_value, max_value, step)
	stream_lines = generate_stream_lines(X, Y, Ex, Ey, *argv, **kwargs)
	stream_arrows = generate_stream_arrows(stream_lines)
	return Streamplot(stream_lines, stream_arrows)

def write_streamplot(directory, streamplot):
	try:
		os.mkdir(directory)
	except FileExistsError as err:
		print('The directory provided already exists.')
		sys.exit('Program terminating.')
	except FileNotFoundError as err:
		print('Parent directory does not exist.')
		sys.exit('Program terminating.')
	
	streamlines_file = os.path.join(directory, 'streamlines.dat')
	write_stream_lines(str(streamlines_file), streamplot.streamlines)
	
	streamarrows_file = os.path.join(directory, 'streamarrows.dat')
	write_stream_arrows(str(streamarrows_file), streamplot.streamarrows)

def main():
	f = lambda X, Y : ((X + 1)/((X+1)**2 + Y**2) - (X - 1)/((X-1)**2 + Y**2), Y/((X+1)**2 + Y**2) - Y/((X-1)**2 + Y**2))
	streamplot = create_streamplot( f, (-5,-5), (5,5), (0.1, 0.1), density=1.4)
	write_streamplot('streamplot', streamplot)

def test():
	streamline_segments = [
		np.array([[1.0, 0.0], [2.0, 0.0]]),
		np.array([[2.0, 0.0], [3.0, 0.0]]),
		np.array([[0.0, 0.0], [1.0, 0.0]]),
		np.array([[0.0, 1.0], [1.0, 1.0]]),
		np.array([[1.0, 1.0], [2.0, 1.0]]),
		np.array([[2.0, 1.0], [3.0, 1.0]])
		]
	stream_lines = segments_to_streamlines(streamline_segments)

if __name__ == '__main__':
	main()
