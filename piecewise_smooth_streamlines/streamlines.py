import numpy as np
import matplotlib.pyplot as plt
import bitstring as btstr

import abc

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

class _LineEdgesMap:
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

class Meshgrid:
	def __init__(self, X, Y, Fx, Fy):
		self.X = X
		self.Y = Y
		self.Fx = Fx
		self.Fy = Fy

class MeshgridGenerator(abc.ABC):
	@abc.abstractmethod
	def get_meshgrid(self, vector_field):
		pass

class IsoMeshgridGenerator(MeshgridGenerator):
	def __init__(self, min_value, max_value, step):
		self.min_value = min_value
		self.max_value = max_value
		self.step = step
	
	def get_meshgrid(self, vector_field):
		min_value = self.min_value
		max_value = self.max_value
		step = self.step
		
		x = np.arange(min_value[0], max_value[0], step[0])
		y = np.arange(min_value[1], max_value[1], step[1])
		
		# Meshgrid
		X, Y = np.meshgrid(x, y)
		
		# Assign vector directions
		Fx, Fy = vector_field(X, Y)
		
		return Meshgrid(X, Y, Fx, Fy)

def __get_key_of_point(point):
	c0 = btstr.BitArray(float=point[0], length=64).hex
	c1 = btstr.BitArray(float=point[1], length=64).hex
	return (c0, c1)

def __get_key_of_segment(segment):
	k_begin = __get_key_of_point(segment[0,:])
	k_end = __get_key_of_point(segment[1,:])
	
	return (k_begin, k_end)

def __connect_two_lines_with_segment(line_edges_map, connecting_segment_key):
	connecting_segment_start_key, connecting_segment_end_key = connecting_segment_key
	back_line_part_key, back_line_part = line_edges_map.pop_front(connecting_segment_end_key)
	front_line_part_key, front_line_part = line_edges_map.pop_back(connecting_segment_start_key)
	front_line_part.append_back(back_line_part)
	front_line_part_start_key, _ = front_line_part_key
	_, back_line_part_end_key = back_line_part_key
	line_edges_map.insert((front_line_part_start_key, back_line_part_end_key), front_line_part)

def __extend_line_front_with_segment(line_edges_map, segment, segment_key):
	segment_start_key, segment_end_key = segment_key
	line_key, line = line_edges_map.pop_front(segment_end_key)
	segment_start_point = segment[0,:]
	line.push_front(segment_start_point)
	_, line_end_key = line_key
	line_edges_map.insert((segment_start_key, line_end_key), line)

def __extend_line_back_with_segment(line_edges_map, segment, segment_key):
	segment_start_key, segment_end_key = segment_key
	line_key, line = line_edges_map.pop_back(segment_start_key)
	segment_end_point = segment[1,:]
	line.push_back(segment_end_point)
	line_start_key, _ = line_key
	line_edges_map.insert((line_start_key, segment_end_key), line)

def __create_new_line(line_edges_map, segment, segment_key):
	line = struct.Dequeue()
	line.push_front(segment[0,:])
	line.push_back(segment[1,:])
	line_edges_map.insert(segment_key, line)

def __insert_segment_in_lines(line_edges_map, segment):
	segment_key = __get_key_of_segment(segment)
	segment_start_key, segment_end_key = segment_key
	
	if line_edges_map.exists_line_begining_with(segment_end_key):
		if line_edges_map.exists_line_ending_with(segment_start_key):
			__connect_two_lines_with_segment(line_edges_map, segment_key)
		else:
			__extend_line_front_with_segment(line_edges_map, segment, segment_key)
	elif line_edges_map.exists_line_ending_with(segment_start_key):
		__extend_line_back_with_segment(line_edges_map, segment, segment_key)
	else:
		__create_new_line(line_edges_map, segment, segment_key)

def __convert_LineEdgesMap_to_List(line_segments):
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

def __is_singular(segment):
	k_begin, k_end = __get_key_of_segment(segment)
	return k_begin == k_end

def __segments_to_streamlines(segments):
	non_singular_segments = filter(lambda segment : not(__is_singular(segment)), segments)
	
	lines = _LineEdgesMap()
	for segment in non_singular_segments:
		__insert_segment_in_lines(lines, segment)
	
	stream_lines = __convert_LineEdgesMap_to_List(lines)
	
	return stream_lines

def generate_stream_lines(meshgrid, *argv, **kwargs):
	X, Y = (meshgrid.X, meshgrid.Y)
	Fx, Fy = (meshgrid.Fx, meshgrid.Fy)
	
	# Depict illustration
	streamlines = plt.streamplot(X, Y, Fx, Fy, *argv, **kwargs)
	line_segments = streamlines.lines.get_segments()
	
	stream_lines = __segments_to_streamlines(line_segments)

	return stream_lines

def __get_cumulative_distances_along_line_points(line):
	cumulative_length = 0.0
	length_up_to_point = []
	previous_point = None
	
	for point in line:
		if previous_point is None:
			distance = 0.0
		else:
			distance = np.linalg.norm(point - previous_point)
		
		cumulative_length = cumulative_length + distance
		length_up_to_point.append(cumulative_length)
		previous_point = point

	return length_up_to_point

def __expand_arrow_up_to_the_closest_segment_edge(position_factor_along_segment, min_arrow_extension_factor):
	arrow_extension_factor = min( position_factor_along_segment, 1 - position_factor_along_segment )
	arrow_extension_factor = max( min_arrow_extension_factor, arrow_extension_factor )
	
	return arrow_extension_factor

def __get_arrow_segment(start, segment_vector, midpoint_position_factor, arrow_extension_factor):
	mid_point = start + midpoint_position_factor * segment_vector
	
	start_point = mid_point - arrow_extension_factor * segment_vector
	end_point = mid_point + arrow_extension_factor * segment_vector
	
	return (start_point, mid_point, end_point)

def __get_line_midpoint_arrow(line, min_arrow_extension_factor = 0.01):
	if len(line) < 2:
		return None
	
	length_up_to_point = __get_cumulative_distances_along_line_points(line)
	
	total_length = length_up_to_point[-1]
	half_length = 0.5 * total_length
	
	def get_index_of_last_point_before_line_half_length():
		n = np.searchsorted(length_up_to_point, half_length, side = 'left')
		# length_up_to_point[n-1] < half_length <= length_up_to_point[n]
		n = n - 1
		# length_up_to_point[n] < half_length <= length_up_to_point[n+1]
		return n
	
	n = get_index_of_last_point_before_line_half_length()
	
	midpoint_position_factor_along_the_segmen_at_the_line_half_length = (half_length - length_up_to_point[n]) / (length_up_to_point[n+1] - length_up_to_point[n])
	arrow_extension_factor = __expand_arrow_up_to_the_closest_segment_edge(midpoint_position_factor_along_the_segmen_at_the_line_half_length, min_arrow_extension_factor)
			
	return __get_arrow_segment(line[n],
		line[n+1] - line[n],
		midpoint_position_factor_along_the_segmen_at_the_line_half_length,
		arrow_extension_factor)

def generate_stream_arrows(stream_lines):
	return list(map(__get_line_midpoint_arrow, stream_lines))

def __write_stream_lines(filename, stream_lines):
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

def __write_stream_arrows(filename, arrows):
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

def generate_streamplot(vector_field, meshgrid_generator, *argv, **kwargs):
	meshgrid = meshgrid_generator.get_meshgrid(vector_field)
	stream_lines = generate_stream_lines(meshgrid, *argv, **kwargs)
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
	__write_stream_lines(str(streamlines_file), streamplot.streamlines)
	
	streamarrows_file = os.path.join(directory, 'streamarrows.dat')
	__write_stream_arrows(str(streamarrows_file), streamplot.streamarrows)

def main():
	f = lambda X, Y : ((X + 1)/((X+1)**2 + Y**2) - (X - 1)/((X-1)**2 + Y**2), Y/((X+1)**2 + Y**2) - Y/((X-1)**2 + Y**2))
	meshgrid_generator = IsoMeshgridGenerator(min_value=(-5,-5), max_value=(5,5), step=(0.1, 0.1))
	streamplot = generate_streamplot( f, meshgrid_generator, density=1.4)
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
	stream_lines = __segments_to_streamlines(streamline_segments)

if __name__ == '__main__':
	main()
