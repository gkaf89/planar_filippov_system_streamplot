import numpy as np
import streamlines

class FilipovPlanarField:
	def __init__(self, vector_field_0, vector_field_1, manifold):
		self.__vector_field_0 = vector_field_0
		self.__vector_field_1 = vector_field_1
		self.__manifold = manifold
	
	def phase_planes(self, min_value, max_value, step):
		# 1D arrays
		x = np.arange(min_value[0], max_value[0], step[0])
		y = np.arange(min_value[1], max_value[1], step[1])
		
		# Meshgrid
		X, Y = np.meshgrid(x, y)
		
		# Assign vector direction
		Fx_0, Fy_0 = self.__vector_field_0(X, Y)
		Fx_1, Fy_1 = self.__vector_field_1(X, Y)
		S = self.__manifold(X,Y)
		
		return (X, Y, Fx_0, Fy_0, Fx_1, Fy_1, S)
	
	@classmethod
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

	
