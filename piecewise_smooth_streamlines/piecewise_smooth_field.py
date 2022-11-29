import numpy as np
import streamlines as streamlines

import matplotlib.pyplot as plt
from scipy.optimize import fsolve

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

def filter_line(line, u, manifold):
	alpha = - (2*u - 1)
	filtered_line = []
	
	idx = 0
	crossed_manifold = False
	while idx < len(line) and not(crossed_manifold):
		point = line[idx]
		if alpha*manifold(point[0], point[1]) > 0:
			filtered_line.append(point)
			idx = idx + 1
		else:
			crossed_manifold = True
	
	if crossed_manifold and idx > 0:
		dx = line[idx] - line[idx-1]
		x_0 = line[idx-1]
		
		def linear_approximation(t):
			return x_0 + t*dx
		
		t_0 = fsolve(lambda t : alpha*manifold(linear_approximation(t)), 0.5)
		final_point = linear_approximation(t_0)
		
		filtered_line.append(final_point)
	
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
