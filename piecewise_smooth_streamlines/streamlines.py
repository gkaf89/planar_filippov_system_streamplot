import numpy as np
import matplotlib.pyplot as plt
import bitstring as btstr

import sys
import os

import piecewise_smooth_streamlines.datastructures as struct

def phase_plane(vector_field, min_value, max_value, step):
	# 1D arrays
	x = np.arange(min_value[0], max_value[0], step[0])
	y = np.arange(min_value[1], max_value[1], step[1])
	
	# Meshgrid
	X, Y = np.meshgrid(x, y)
	
	# Assign vector directions
	Ex, Ey = vector_field(X, Y)
	
	return (X, Y, Ex, Ey) 

def generate_stream_lines(X, Y, Ex, Ey, *argv, **kwargs):
	# Depict illustration
	streamlines = plt.streamplot(X, Y, Ex, Ey, *argv, **kwargs)
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
			extendable_segment = struct.Dequeue()
			extendable_segment.push_front(end_point)
			extendable_segment.push_back(start_point)
			segments_end[key_point_end] = extendable_segment
			segments_start[key_point_start] = extendable_segment
	
	stream_lines = []
	for segment_key in segments_start:
		stream_line = []
		segment = segments_start[segment_key]
		while not segment.empty():
			point = segment.back()
			stream_line.append(point)
			segment.pop_back()
		stream_lines.append(stream_line)
	
	return stream_lines

def _cumulative_distance(line):
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

def _ensure_minimum_edge_separation(location_fraction, min_edge_fraction):
	location_fraction = max( min_edge_fraction, location_fraction )
	location_fraction = min( 1 - min_edge_fraction, location_fraction )
	
	return location_fraction

def find_midpoint(line, min_edge_fraction = 0.01):
	if len(line) < 2:
		return None
	
	lengths = _cumulative_distance(line)
	total_length = lengths[-1]
	
	mid_length = 0.5 * total_length
	
	for n in range(0, len(line)-1):
		if lengths[n+1] > mid_length:
			distance = lengths[n+1] - lengths[n]
			difference = mid_length - lengths[n]
			
			location_fraction = difference/distance
			location_fraction = _ensure_minimum_edge_separation(location_fraction, min_edge_fraction)
			
			end_point_fraction = min( location_fraction, 1 - location_fraction )
			
			displacement = line[n+1] - line[n]
			
			mid_segment = line[n] + location_fraction * displacement
			initial_point = mid_segment - end_point_fraction * displacement
			final_point = mid_segment + end_point_fraction * displacement
			
			return (initial_point, mid_segment, final_point)
	
	return None

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
			file.write('\n')

class Streamplot:
	def __init__(self, streamlines, streamarrows):
		self.streamlines = streamlines
		self.streamarrows = streamarrows

def create_streamplot(vector_field, min_value, max_value, step, *argv, **kwargs):
	X,Y,Ex,Ey = phase_plane(vector_field, min_value, max_value, step)
	stream_lines = generate_stream_lines(X,Y,Ex,Ey, *argv, **kwargs) 
	stream_arrows = list(map(find_midpoint, stream_lines))
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

if __name__ == '__main__':
	main()
