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

#ifndef _DELTAV_H
#define _DELTAV_H 1

// Calculates deltaV (electrostatic interactions) between molecules
double Calcul_DeltaV(int i, int mol_index_tmp, int neigh_index_tmp, int neigh_num_tmp,\
							unsigned int charge_i_tmp, vector<int> curr_mol_tmp, vector<int> curr_box_tmp);

// Calculates V (electrostatic interactions) for a charge
double Calcul_V(int i, int mol_index_tmp, unsigned int charge_i_tmp, vector<int> curr_mol_tmp,\
																					vector<int> curr_box_tmp);
	
#endif // deltav.h
