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
	
	meshgrid_0 = streamlines.Meshgrid(X, Y, Fx_0, Fy_0)
	meshgrid_1 = streamlines.Meshgrid(X, Y, Fx_1, Fy_1)
	
	stream_lines_0 = streamlines.generate_stream_lines(meshgrid_0, *argv, **kwargs)
	stream_lines_1 = streamlines.generate_stream_lines(meshgrid_1, *argv, **kwargs)
	
	return (stream_lines_0, stream_lines_1)

def control_active_on_negative(x, u, manifold):
	alpha = - (2*u - 1)
	return alpha * manifold(x[0], x[1]) >= 0

# Indepotent function
def drop_invisible_subsequence(line, u, manifold, idx):
	while idx < len(line) and not(control_active_on_negative(line[idx], u, manifold)):
		idx = idx + 1
	
	return idx

# Indepotent function
def extract_visible_subsequence(line, u, manifold, idx, visible_line_section):
	while idx < len(line) and control_active_on_negative(line[idx], u, manifold):
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

def append_crossing_point(line, manifold, idx, visible_line_section):
	if not(visible_line_section):
		return
	
	if idx >= len(line):
		return
	
	x_0 = visible_line_section[-1]
	x_1 = line[idx]
	
	x_t = get_crossing_point(manifold, x_0, x_1)
	
	visible_line_section.append(x_t);

def prepend_crossing_point(line, manifold, idx, visible_line_section):
	if idx >= len(line):
		return
	
	if idx < 1:
		return
	
	x_0 = line[idx-1]
	x_1 = line[idx]
	
	x_t = get_crossing_point(manifold, x_0, x_1)
	
	visible_line_section.append(x_t);

def filter_stream_line(line, u, manifold):
	visible_line_section = []
	
	idx = 0
	while idx < len(line):
		idx = extract_visible_subsequence(line, u, manifold, idx, visible_line_section)
		append_crossing_point(line, manifold, idx, visible_line_section)
		idx = drop_invisible_subsequence(line, u, manifold, idx)
		prepend_crossing_point(line, manifold, idx, visible_line_section)
	
	return visible_line_section

class PiecewiseBifield:
	def __init__(self, vector_field_0, vector_field_1, manifold):
		self.vector_field_0 = vector_field_0
		self.vector_field_1 = vector_field_1
		self.manifold = manifold

class PiecewiseBifieldStreamplot:
	def __init__(self, piecewiseBifield, piecewiseBifieldMeshgridGenerator):
		self.piecewise_bifield_meshgrid = piecewiseBifieldMeshgridGenerator.get_piecewise_bifiled_meshgrid(
			piecewiseBifield.vector_field_0,
			piecewiseBifield.vector_field_1,
			piecewiseBifield.manifold
		)
		self.piecewise_bifield = piecewiseBifield
	
	def generate_stream_lines(self, *argv, **kwargs):
		(extended_stream_lines_0, extended_stream_lines_1) = generate_extended_stream_lines(self.piecewise_bifield_meshgrid, *argv, **kwargs)
		
		def filter_with_control_inactive(line):
			return filter_stream_line(line, 0, self.piecewise_bifield.manifold)
		
		def filter_with_control_active(line):
			return filter_stream_line(line, 1, self.piecewise_bifield.manifold)
		
		stream_lines_0 = map(filter_with_control_inactive, extended_stream_lines_0)
		stream_lines_1 = map(filter_with_control_active, extended_stream_lines_1)
		
		return (stream_lines_0, stream_lines_1)
		
	@staticmethod
	def generate_contour_plot(X, Y, S, level, **kwargs):
		contours = plt.contour(X, Y, S, [level], **kwargs)
		paths = contours.collections[0].get_paths() # single 'level' present
		
		contour_lines = map( lambda path : path.vertices, paths)
		
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

class BifieldStreamplot:
	def __init__(self,
			  streamlines_0, streamlines_1,
			  streamarrows_0, streamarrows_1,
			  switching_manifold):
		self.streamlines_0 = streamlines_0
		self.streamlines_1 = streamlines_1
		self.streamarrows_0 = streamarrows_0
		self.streamarrows_1 = streamarrows_1
		self.switching_manifold = switching_manifold

class NonConformantKeyword(Exception):
	def __init__(self, non_conformant_keyword, *args):
		super().__init__(*args)
		self.non_conformant_keyword = non_conformant_keyword
	
	def __str__(self):
		return f"The keyword {self.non_conformant_keyword} is not of the form <target command>_<payload>"

class UnkownTarget(Exception):
	def __init__(self, unknown_target, *args):
		super().__init__(*args)
		self.unknown_target = unknown_target
	
	def __str__(self):
		return f"The target {self.unknown_target} is not known"

def get_keywords(**kwargs):
	keywords = {**kwargs}
	
	stream_kwargs = {}
	manifold_kwargs = {}
	for key in keywords:
		parts = key.split("_", 1)
		if len(parts) != 2:
			raise NonConformantKeyword(key)
		
		target = parts[0]
		keyword = parts[1]
		
		if target == 'stream':
			stream_kwargs[keyword] = keywords[key]
		elif target == 'manifold':
			manifold_kwargs[keyword] = keywords[key]
		else:
			raise UnkownTarget(target)
		
	return (stream_kwargs, manifold_kwargs)

def generate_stream_plot(piecewiseBifield, piecewiseBifieldMeshgridGenerator, *argv, **kwargs):
	try:
		keyword_arguments = {**kwargs}
		(stream_kwargs, manifold_kwargs) = get_keywords(**keyword_arguments)
		
		piecewise_bifield_streamplot = PiecewiseBifieldStreamplot(piecewiseBifield, piecewiseBifieldMeshgridGenerator)
		(stream_lines_0, stream_lines_1) = piecewise_bifield_streamplot.generate_stream_lines(*argv, **stream_kwargs)
		
		stream_arrows_0 = streamlines.generate_stream_arrows(stream_lines_0)
		stream_arrows_1 = streamlines.generate_stream_arrows(stream_lines_1)
		
		switching_manifold = piecewise_bifield_streamplot.generate_switching_manifold(**manifold_kwargs)
		
		return BifieldStreamplot(
				stream_lines_0, stream_lines_1,
				stream_arrows_0, stream_arrows_1,
				switching_manifold
			)
	except NonConformantKeyword as non_conformant_keyword:
		raise non_conformant_keyword
	except UnkownTarget as unkown_target:
		raise unkown_target
	

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
