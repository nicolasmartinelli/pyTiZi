/**
 *******************************************************************************
 * Copyright (C) 2010 Nicolas Martinelli, nicolas.martinelli@gmail.com         *
 * This library is part of the MC_BKL and MC_BKL_layer software                *
 *                                                                             *
 * This program is free software: you can redistribute it and/or modify        *
 * it under the terms of the GNU General Public License as published by        *
 * the Free Software Foundation, either version 3 of the License, or           *
 * (at your option) any later version.                                         *
 *                                                                             *
 * This program is distributed in the hope that it will be useful,             *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of              *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               *
 * GNU General Public License for more details.                                *
 *                                                                             *
 * You should have received a copy of the GNU General Public License           *
 * along with this program.  If not, see <http://www.gnu.org/licenses/>        *
 *******************************************************************************
 */

#ifndef _VARIABLES_H
#define _VARIABLES_H 1

#ifdef _INSIDE_MC_BKL
#define EXTERN
#else
#define EXTERN extern
#endif

// C++ libraries
#include <ctime>
#include <string>
#include <vector>

using namespace std;

// Variables read in the input file
EXTERN int n_frame, n_mol; // Number of frame and molecule
EXTERN double snap_delay;
EXTERN double LAMBDA_I, LAMBDA_I_H, LAMBDA_I_E, LAMBDA_S, T, H_OMEGA, dist_tot;
EXTERN unsigned int n_try, n_charges;
EXTERN int n_box_a, n_box_b, n_box_c;
EXTERN double F_norm; 
EXTERN string F_dir;
EXTERN string charge;

EXTERN int n_box;

// Variables for the unit cell parameters
EXTERN bool pbc[3];																// Periodic boundary cond.
EXTERN vector<double> a, b, c, alpha_deg, beta_deg, gamma_deg, vol_box; 		// Cell parameters
EXTERN vector<double> temp_alpha_cos, temp_beta_sin, temp_beta_cos,\
               temp_gamma_sin, temp_gamma_cos, temp_beta_term, temp_gamma_term; // Params for fractional coord

// Variables for each molecule
EXTERN vector<int> mol_label;
EXTERN vector< vector<double> > CM_x, CM_y, CM_z;								// Center of masses
EXTERN vector< vector<double> > E_0, E_1;										// Site energies if box
																				// [frame][molecule]
EXTERN vector< vector< vector<double> > > E_grid;								// Site energies if grid
																				// [frame][box][molecule]

// Variables for each charge
EXTERN vector< vector< vector<double> > > chrg_E_electrostatic, chrg_E_0, chrg_E_1;
																				// [frame][charge][jump]
EXTERN vector< vector<double> > chrg_total_time, chrg_total_dist;				// [frame][charge]

// Variables for the grid
// grid_ is used for a detailed table (frame/box/molecule)
// box_ is used for a box parameters (relative position between 2 boxes)
EXTERN vector<int> box_a, box_b, box_c; 										// Position of the mini-grids
EXTERN vector< vector<int> > box_neigh_a, box_neigh_b, box_neigh_c, box_neigh_label;
																				// Neighbor of each mini-grid
EXTERN vector< vector<bool> > grid_occ;											// Occupation of each site
EXTERN vector< vector< vector< vector <double> > > > grid_probability; 			// Occupation probability 
																				// of each site
EXTERN vector< vector< vector <double> > > grid_x, grid_y, grid_z;				// Coordinates of each site
EXTERN vector< vector< vector <double> > > grid_E_0, grid_E_1;					// Energy of each site
EXTERN string grid_E_type;
EXTERN double grid_sigma_over_kT;
EXTERN double grid_radius_sphere;
EXTERN double grid_e_max_sphere, grid_e_decrease_sphere;

// Variables for neighbors
EXTERN vector< vector< vector<int> > > neigh_label;					// Label of neighbors
EXTERN vector< vector< vector<double> > > d_x, d_y, d_z;			// Distance
EXTERN vector< vector< vector<double> > > dE_box;					// Delta E if distributed in box
EXTERN vector< vector< vector< vector<double> > > > dE_grid;		// Delta E if distributed in grid
EXTERN vector< vector< vector<double> > > J_H, J_L;					// Transfer integrals
EXTERN vector< vector< vector<int> > > neigh_jump_vec_a, neigh_jump_vec_b, neigh_jump_vec_c;
																	// Vect. for mini-grid change
EXTERN vector< vector< vector<double> > > k, k_inv;					// Transf. rates and inverse

// Variables for the electric field direction
//double theta_deg, phi_deg, theta_rad, phi_rad;
EXTERN vector<double>  F_x_list, F_y_list, F_z_list, F_angle_list;
EXTERN double F_x, F_y, F_z, F_angle;
EXTERN bool anisotropy;

// Variable for calculation of electrostatic interactions and transfer rate
EXTERN string transfer;
EXTERN bool coulomb;

// Constants for the MLJ theory
EXTERN double S, MLJ_CST1, MLJ_CST2; 
EXTERN vector <double> MLJ_CST3;

// Variables for Layer
EXTERN int n_layer;																// Total number of layers
EXTERN int layer;																// Layer to run the simulation
EXTERN vector<double> min_layer;
EXTERN vector<double> max_layer;
EXTERN vector< vector< vector<int> > > mol_layer;
EXTERN vector< vector<int> > list_layer;

// Time variables
EXTERN time_t t_info;
EXTERN string t_info_str;

#endif // variables.h
