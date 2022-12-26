import numpy as np
import abc

import matplotlib.pyplot as plt
from scipy.optimize import fsolve
import functools
import tail_recursive

import streamlines as streamlines

# See: https://stackoverflow.com/questions/5666056/matplotlib-extracting-data-from-contour-lines

class PiecewiseBifieldMeshgrid:
	def __init__(self, X, Y, Fx_0, Fy_0, Fx_1, Fy_1, S):
		self.X = X
		self.Y = Y
		self.Fx_0 = Fx_0
		self.Fy_0 = Fy_0
		self.Fx_1 = Fx_1
		self.Fy_1 = Fy_1
		self.S = S

class PiecewiseBifieldMeshgridGenerator(abc.ABC):
	@abc.abstractmethod
	def get_piecewise_bifiled_meshgrid(self, vector_field_0, vector_field_1, switching_manifold):
		pass

class IsoPiecewiseBifieldMeshgridGenerator(PiecewiseBifieldMeshgridGenerator):
	def __init__(self, min_value, max_value, step):
		self.min_value = min_value
		self.max_value = max_value
		self.step = step
	
	def get_piecewise_bifiled_meshgrid(self, vector_field_0, vector_field_1, switching_manifold):
		min_value = self.min_value
		max_value = self.max_value
		step = self.step
		
		# 1D arrays
		x = np.arange(min_value[0], max_value[0], step[0])
		y = np.arange(min_value[1], max_value[1], step[1])
		
		# Meshgrid
		X, Y = np.meshgrid(x, y)
		
		# Assign vector directions
		Fx_0, Fy_0 = vector_field_0(X, Y)
		Fx_1, Fy_1 = vector_field_1(X, Y)
		S = switching_manifold(X, Y)
		
		return PiecewiseBifieldMeshgrid(X, Y, Fx_0, Fy_0, Fx_1, Fy_1, S)

def generate_extended_stream_lines(piecewiseBifieldMeshgrid, *argv, **kwargs):
	X, Y = (piecewiseBifieldMeshgrid.X, piecewiseBifieldMeshgrid.Y)
	Fx_0, Fy_0 = (piecewiseBifieldMeshgrid.Fx_0, piecewiseBifieldMeshgrid.Fy_0)
	Fx_1, Fy_1 = (piecewiseBifieldMeshgrid.Fx_1, piecewiseBifieldMeshgrid.Fy_1)
	
	messgrid_0 = Meshgrid(X, Y, Fx_0, Fy_0)
	messgrid_1 = Meshgrid(X, Y, Fx_1, Fy_1)
	
	stream_lines_0 = streamlines.generate_stream_lines(meshgrid_0, *argv, **kwargs):
	stream_lines_1 = streamlines.generate_stream_lines(meshgrid_1, *argv, **kwargs):
	
	return (stream_lines_0, stream_lines_1)

def dynamics_is_vissible(x, u, manifold):
	alpha = - (2*u - 1)
	return alpha * manifold(x[0], x[1]) >= 0

# Indepotent function
def drop_negative_sequence(line, u, manifold, idx):
	while idx < len(line) and not(dynamics_is_vissible(line[idx], u, manifold)):
		idx = idx + 1
	
	return idx

# Indepotent function
def extract_positive_subsequence(line, u, manifold, idx, visible_line_section):
	while idx < len(line) and dynamics_is_vissible(line[idx], u, manifold):
		x = line[idx]
		visible_line_section.apend(x)
		idx = idx + 1
	
	return idx

def get_crossing_point(manifold, x_0, x_1):
	dx = x_1 - x_0
	
	def linear_approximation(t):
		return x_0 + t*dx
	
	t_0 = fsolve(lambda t : manifold(linear_approximation(t)), 0.5)
	
	return linear_approximation(t_0)

def postappend_crossing_point(line, manifold, idx, visible_line_section):
	if not(visible_line_section):
		return
	
	if idx >= len(line):
		return
	
	x_0 = visible_line_section[-1]
	x_1 = line[idx]
	
	x_t = get_crossing_point(manifold, x_0, x_1)
	
	visible_line_section.append(linear_approximation(x_t));

def preappend_crossing_point(line, manifold, idx, visible_line_section):
	if idx >= len(line):
		return
	
	if idx < 1:
		return
	
	x_0 = line[idx-1]
	x_1 = line[idx]
	
	x_t = get_crossing_point(manifold, x_0, x_1)
	
	visible_line_section.append(linear_approximation(x_t));

def filter_stream_line(line, u, manifold):
	visible_line_section = []
	
	idx = 0
	while idx < len(line):
		idx = extract_positive_subsequence(line, u, manifold, idx, visible_line_section)
		postappend_crossing_point(line, manifold, idx, visible_line_section)
		idx = drop_negative_sequence(line, u, manifold, idx)
		preappend_crossing_point(line, manifold, idx, visible_line_section)
	
	return filtered_line

def filer_stream_lines(stream_lines, u, manifold):
	filtered_stream_lines = []
	for line in stream_lines:
		filtered_stream_lines.append(filter_stream_line(line, u, manifold))
	
	return filtered_stream_lines

class PiecewiseBifield:
	def __init__(self, vector_field_0, vector_field_1, manifold):
		self.vector_field_0 = vector_field_0
		self.vector_field_1 = vector_field_1
		self.manifold = manifold

class PiecewiseBifieldStreamplot:
	def __init__(piecewiseBifield, piecewiseBifieldMeshgridGenerator):
		self.piecewise_bifield_meshgrid = piecewiseBifieldMeshgridGenerator.get_piecewise_bifiled_meshgrid(
			piecewiseBifield.vector_field_0,
			piecewiseBifield.vector_field_1,
			piecewiseBifield.manifold
		)
		self.piecewise_bifield = piecewiseBifield
		
		def generate_stream_lines(self, *argv, **kwargs):
			(extended_stream_lines_0, extended_stream_lines_1) = generate_extended_stream_lines(self.piecewise_bifield_meshgrid, *argv, **kwargs)
			
			stream_lines_0 = filtered_stream_lines(extended_stream_lines_0, 0, self.piecewise_bifield.manifold)
			stream_lines_1 = filtered_stream_lines(extended_stream_lines_1, 1, self.piecewise_bifield.manifold)
			
			return (stream_lines_0, stream_lines_1)
		
		@staticmethod
		def generate_contour_plot(X, Y, S, level, **kwargs):
			contours = plt.contour(X, Y, S, levels = [level], **kwargs)
			paths = contours.collections[0].get_paths()
			
			contour_lines = []
			for path in paths:
				line = path.vertices
				contour_lines.append(line)
			
			return contour_lines
		
		def generate_switching_manifold(self, **kwargs):
			level = 0.0
			contour_lines = PiecewiseBifieldStreamplot.generate_contour_plot(
				self.piecewise_bifield_meshgrid.X,
				self.piecewise_bifield_meshgrid.Y,
				self.piecewise_bifield_meshgrid.S,
				level,
				**kwargs
			)
			
			return contour_lines
		
		def generate_stream_arrows(stream_lines_0, stream_lines_1):
			stream_arrows_0 = streamlines.generate_stream_arrows(stream_lines_0)
			stream_arrows_1 = streamlines.generate_stream_arrows(stream_lines_1)
			
			return (stream_arrows_0, stream_arrows_1)

def test_plot(self):
	plt.figure(figsize=(10, 10))
	plt.streamplot(self.__X, self.__Y, self.__Fx_0, self.__Fy_0, density=1.4, linewidth=None, color='#A23BEC')
	plt.plot(-1,0,'-or')
	plt.plot(1,0,'-og')
	plt.title('Field 0')

	# Show plot with grid
	plt.grid()
	plt.show()

	plt.figure(figsize=(10, 10))
	plt.streamplot(self.__X, self.__Y, self.__Fx_1, self.__Fy_1, density=1.4, linewidth=None, color='#A23BEC')
	plt.plot(-1,0,'-or')
	plt.plot(1,0,'-og')
	plt.title('Field 1')

	# Show plot with grid
	plt.grid()
	plt.show()
