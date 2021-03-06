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

#ifndef _DELTAE_H
#define _DELTAE_H 1

// Generate a Gaussian DOS
void Generate_Gaussian_DOS(double mean, double sigma, bool print_results);

// Generate a Correlated DOS
void Generate_Correlated_DOS(double sigma, bool print_results);

// Generate a hard sphere DOS
void Generate_Hard_Sphere_DOS(double radius, bool print_results);

// Generate a exponential sphere DOS
void Generate_Exponential_Sphere_DOS(double E_max, double E_decrease, bool print_results);

// Generate a 1/r sphere DOS
void Generate_Over_R_Sphere_DOS(double E_max, double E_decrease, bool print_results);

// Set the variable dE to zero
void DeltaE_ZERO(bool print_results);

// Calculates deltaE between molecules for a distribution in the box
void Calcul_DeltaE(bool print_results);

// Calculates deltaE between molecules for a distribution in the grid
void Calcul_DeltaE_GRID(bool print_results);

#endif // deltae.h
