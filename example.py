import piecewise_smooth_streamlines.piecewise_smooth_field as pws
import piecewise_smooth_streamlines.streamlines as streamlines

def bridge_converter(L, C, n, v_in, R):
	def converter_controller(u):
		def f(i_L, v_C):
			D_i_L = (1/L)*(-n*(u(2) - u(3))*v_C + (u(0) - u(1))*v_in)
			D_v_C = (1/C)*((1/n)*(u(2)-u(3))*i_L - v_C/R)
			return (D_i_L, D_v_C)
		return f
	return converter_controller

def main():
	C = 114.7e-6
	L = 5.25e-6
	n = 10/50
	v_in = 270
	v_out = 28
	P = 324
	# P = v_out * (v_out/R)
	R = (v_out**2)/P
	
	controller = bridge_converter(L, C, n, v_in, R)
	vector_field_0 = controller([0,1,1,0])
	vector_field_1 = controller([1,0,0,1])
	
	i_out = n*(v_out/v_in)*(n*v_out + v_in)/R
	u_out = n*v_out/(n*v_out + v_in)
	alpha= 1/2
	
	manifold = lambda x : (1/(n*C))*(1-u_out)*x(0) + (alpha - 1/(R*C))*x(1) - alpha*v_out
	
	pws.FilipovPlanarField(vector_field_0, vector_field_1, manifold)

if __name__ == '__main__':
	main()
