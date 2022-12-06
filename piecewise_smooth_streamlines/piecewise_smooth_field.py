import numpy as np

import matplotlib.pyplot as plt
from scipy.optimize import fsolve
import functools
import tail_recursive

import streamlines as streamlines

# See: https://stackoverflow.com/questions/5666056/matplotlib-extracting-data-from-contour-lines

class Meshgrid:
	def __init__(self, X, Y, Fx_0, Fy_0, Fx_1, Fy_1, S):
		self.__X = X
		self.__Y = Y
		self.__Fx_0 = Fx_0
		self.__Fy_0 = Fy_0
		self.__Fx_1 = Fx_1
		self.__Fy_1 = Fy_1
		self.__S = S

	def generate_stream_lines(self, *args, **kwargs):
		stream_lines_0 = streamlines.generate_stream_lines(self.__X, self.__Y, self.__Fx_0, self.__Fy_0, *args, **kwargs)
		stream_lines_1 = streamlines.generate_stream_lines(self.__X, self.__Y, self.__Fx_1, self.__Fy_1, *args, **kwargs)
		return (stream_lines_0, stream_lines_1)

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

def signed_manifold(x, u, manifold):
	alpha = - (2*u - 1)
	return alpha * manifold(x[0], x[1])

# Indepotent function
def drop_negative_sequence(line, u, manifold, idx):
	while idx < len(line) and signed_manifold(line[idx], u, manifold) < 0:
		idx = idx + 1

# Indepotent function
def extract_positive_subsequence(line, u, manifold, idx, visible_line_section):
	while idx < len(line) and signed_manifold(line[idx], u, manifold) > 0:
		x = line[idx]
		visible_line_section.apend(x)
		idx = idx + 1

def get_crossing_point(manifold, x_0, x_1):
	dx = x_1 - x_0
	
	def linear_approximation(t):
		return x_0 + t*dx
	
	t_0 = fsolve(lambda t : manifold(linear_approximation(t)), 0.5)
	
	return linear_approximation(t_0)

def postappend_crossing_point(line, manifold, idx, visible_line_section):
	if visible_line_section:
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

def filter_line(line, u, manifold):
	visible_line_section = []
	
	idx = 0
	while idx < len(line):
		extract_positive_subsequence(line, u, manifold, idx, visible_line_section)
		postappend_crossing_point(line, manifold, idx, visible_line_section)
		drop_negative_sequence(line, u, manifold, idx)
		preappend_crossing_point(line, manifold, idx, visible_line_section)
	
	return filtered_line

def filer_stream_lines(stream_lines, u, manifold):
	filtered_stream_lines = []
	for line in stream_lines:
		filtered_stream_lines.append(filter_line(line, u, manifold))
	
	return filtered_stream_lines

def generate_stream_lines(X, Y, Fx_0, Fy_0, Fx_1, Fy_1, manifold, *argv, **kwargs):
	extended_stream_lines_0 = streamlines.generate_stream_lines(X, Y, Fx_0, Fy_0, argv, kwargs)
	extended_stream_lines_1 = streamlines.generate_stream_lines(X, Y, Fx_1, Fy_1, argv, kwargs)
	
	stream_lines_0 = filtered_stream_lines(extended_stream_lines_0, 0, manifold)
	stream_lines_1 = filtered_stream_lines(extended_stream_lines_1, 1, manifold)
	
	return (stream_lines_0, stream_lines_1)

class PiecewiseSmoothBifield:
	def __init__(self, vector_field_0, vector_field_1, manifold):
		self.__vector_field_0 = vector_field_0
		self.__vector_field_1 = vector_field_1
		self.__manifold = manifold

	def phase_plane_grid(self, min_value, max_value, step):
		# 1D arrays
		x = np.arange(min_value[0], max_value[0], step[0])
		y = np.arange(min_value[1], max_value[1], step[1])

		# Meshgrid
		X, Y = np.meshgrid(x, y)

		# Assign vector direction
		Fx_0, Fy_0 = self.__vector_field_0(X, Y)
		Fx_1, Fy_1 = self.__vector_field_1(X, Y)
		S = self.__manifold(X,Y)

		return Meshgrid(X, Y, Fx_0, Fy_0, Fx_1, Fy_1, S)

	def phase_planes(self, meshgrid, *args, **kwargs):
		stream_lines_0, stream_lines_1 = meshgrid.generate_stream_lines(*args, **kwargs)

		pos_manifold = lambda x : self.__manifold(x[0], x[1]) > 0
		filter_pos_manifold = lambda ls : list(filter(pos_manifold, ls))
		stream_lines_0 = list(map(filter_pos_manifold, stream_lines_0))
		stream_lines_0 = list(filter(lambda ls : len(ls) > 1, stream_lines_0))

		neg_manifold = lambda x : self.__manifold(x[0], x[1]) <= 0
		filter_neg_manifold = lambda ls : list(filter(neg_manifold, ls))
		stream_lines_1 = list(map(filter_neg_manifold, stream_lines_1))
		stream_lines_1 = list(filter(lambda ls : len(ls) > 1, stream_lines_1))

		return (stream_lines_0, stream_lines_1)

	@staticmethod
	def filter_phase_planes(X, Y, Fx_0, Fy_0, Fx_1, Fy_1, S):
		nx, ny = S.shape

		Fx = np.zeros((nx, ny))
		Fy = np.zeros((nx, ny))

		for x in range(nx):
			for y in range(ny):
				if S(x,y) > 0:
					Fx[x,y] = Fx_0[x,y]
					Fy[x,y] = Fy_0[x,y]
				else:
					Fx[x,y] = Fx_1[x,y]
					Fy[x,y] = Fy_1[x,y]

		return (X, Y, Fx, Fy)

	def phase_plane(vector_field, min_value, max_value, step):
		X, Y, Fx_0, Fy_0, Fx_1, Fy_1, S = self.phase_planes(min_value, max_value, step)
		X, Y, Fx, Fy = FilipovPlanarField.filter_phase_planes(X, Y, Fx_0, Fy_0, Fx_1, Fy_1, S)

		return (X, Y, Fx, Fy)
