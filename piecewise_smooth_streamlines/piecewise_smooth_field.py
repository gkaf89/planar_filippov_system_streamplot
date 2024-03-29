import numpy as np
import abc

import matplotlib.pyplot as plt
from scipy.optimize import fsolve

from functools import reduce
# See: tail_recursive

import math

import streamlines as streamlines
import datastructures as struct

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

def _generate_extended_stream_lines(piecewiseBifieldMeshgrid, *argv, **kwargs):
	X, Y = (piecewiseBifieldMeshgrid.X, piecewiseBifieldMeshgrid.Y)
	Fx_0, Fy_0 = (piecewiseBifieldMeshgrid.Fx_0, piecewiseBifieldMeshgrid.Fy_0)
	Fx_1, Fy_1 = (piecewiseBifieldMeshgrid.Fx_1, piecewiseBifieldMeshgrid.Fy_1)
	
	meshgrid_0 = streamlines.Meshgrid(X, Y, Fx_0, Fy_0)
	meshgrid_1 = streamlines.Meshgrid(X, Y, Fx_1, Fy_1)
	
	stream_lines_0 = streamlines.generate_stream_lines(meshgrid_0, *argv, **kwargs)
	stream_lines_1 = streamlines.generate_stream_lines(meshgrid_1, *argv, **kwargs)
	
	return (stream_lines_0, stream_lines_1)

def _control_active_on_negative(x, u, manifold):
	alpha = - (2*u - 1)
	return alpha * manifold(x[0], x[1]) >= 0

# Indepotent function
def _drop_invisible_subsequence(line, u, manifold, idx):
	while idx < len(line) and not(_control_active_on_negative(line[idx], u, manifold)):
		idx = idx + 1
	
	return idx

# Indepotent function
def _extract_visible_subsequence(line, u, manifold, idx, visible_line_section):
	while idx < len(line) and _control_active_on_negative(line[idx], u, manifold):
		x = line[idx]
		visible_line_section.push_front(x)
		idx = idx + 1
	
	return (idx, visible_line_section)

def _get_crossing_point(manifold, x_0, x_1):
	dx = x_1 - x_0
	
	def linear_approximation(t):
		return x_0 + t*dx
	
	def parametrized_planar_manifold(t):
		x = linear_approximation(t)
		return manifold(x[0], x[1])
	
	t_0 = fsolve(parametrized_planar_manifold, 0.5)
	
	return linear_approximation(t_0)

def _extend_edges_to_manifold(line, manifold, begin, end, visible_line_section):
	if visible_line_section.empty() or not(line):
		return visible_line_section
		
	if begin > 0:
		x_0 = line[begin-1]
		x_1 = visible_line_section.back()
		x_t = _get_crossing_point(manifold, x_0, x_1)
		visible_line_section.push_back(x_t)
	
	if end < len(line):
		x_0 = visible_line_section.front()
		x_1 = line[end]
		x_t = _get_crossing_point(manifold, x_0, x_1)
		visible_line_section.push_front(x_t)
	
	return visible_line_section

def _extract_continuous_visible_line_segment(line, u, manifold, idx):
	visible_line_section = struct.Dequeue()
	begin_visible = idx
	
	end_visible, visible_line_section = _extract_visible_subsequence(line, u, manifold, begin_visible, visible_line_section)
	visible_line_section = _extend_edges_to_manifold(line, manifold, begin_visible, end_visible, visible_line_section)
	idx_section_end = _drop_invisible_subsequence(line, u, manifold, end_visible)
	
	return (idx_section_end, visible_line_section.to_list())

def filter_stream_line(line, u, manifold):
	visible_line_sections = []
	idx = 0
	while idx < len(line):
		idx, visible_section = _extract_continuous_visible_line_segment(line, u, manifold, idx)
		if visible_section:
			visible_line_sections.append(visible_section)
	
	return visible_line_sections

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
		(extended_stream_lines_0, extended_stream_lines_1) = _generate_extended_stream_lines(self.piecewise_bifield_meshgrid, *argv, **kwargs)
		
		def filter_with_control_inactive(line):
			return filter_stream_line(line, 0, self.piecewise_bifield.manifold)
		
		def filter_with_control_active(line):
			return filter_stream_line(line, 1, self.piecewise_bifield.manifold)
		
		def get_invisible_line_section_remover(filter_line):
			def remove_invisible_line_section(line_list, line):
				filtered_lines = filter_line(line)
				line_list.extend(filtered_lines)
				return line_list
			
			return remove_invisible_line_section
		
		stream_lines_0 = reduce(
			get_invisible_line_section_remover(filter_with_control_inactive),
			extended_stream_lines_0,
			[]
		)
		stream_lines_1 = reduce(
			get_invisible_line_section_remover(filter_with_control_active),
			extended_stream_lines_1,
			[]
		)
		
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

def generate_streamplot(piecewiseBifield, piecewiseBifieldMeshgridGenerator, *argv, **kwargs):
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

def write_streamplot(directory, bifiled_streamplot):
	lines = {
			   'streamlines_0.dat' : bifiled_streamplot.streamlines_0,
			   'streamlines_1.dat' : bifiled_streamplot.streamlines_1,
			   'switching_manifold.dat' : bifiled_streamplot.switching_manifold,
		    }
	
	arrows = {
				'streamarrows_0.dat' : bifiled_streamplot.streamarrows_0,
				'streamarrows_1.dat' : bifiled_streamplot.streamarrows_1
			 }
	
	streamlines.write_plot_files(directory, lines, arrows)

def main():
	C = 0.6e-3
	L = 1.7e-3
	R = 8
	E = 48
	i_L_s = 4.5
	v_C_s = 36
	phi = math.pi/4
	
	f_0 = lambda i_L, v_C : ((1/L)*(-v_C), (1/C)*(i_L - v_C/R))
	f_1 = lambda i_L, v_C : ((1/L)*(-v_C + E), (1/C)*(i_L - v_C/R))
	
	switching_manifold = lambda i_L, v_C : math.cos(phi)*(i_L - i_L_s) + math.sin(phi)*(v_C - v_C_s)
	
	piecewise_bifield = PiecewiseBifield(f_0, f_1, switching_manifold)
	
	meshgrid_generator = IsoPiecewiseBifieldMeshgridGenerator(min_value=(0,0), max_value=(10,75), step=(0.02, 0.02))
	
	bifield_streamplot = generate_streamplot( piecewise_bifield, meshgrid_generator, stream_density=1.2, stream_broken_streamlines=True)
	write_streamplot('streamplot', bifield_streamplot)

if __name__ == '__main__':
	main()