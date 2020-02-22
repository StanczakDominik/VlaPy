---
title: 'VlaPy: A Python package for Eulerian Vlasov-Poisson-Fokker-Planck Simulations'
tags:
  - Python
  - plasma physics
  - dynamics
  - astrophysics
  - fusion
authors:
  - name: Archis S. Joglekar
    orcid: 0000-0003-3599-5629
    affiliation: "1"
  - name: Matthew C. Levy
    orcid: 0000-0002-7387-0256
    affiliation: "1"
affiliations:
 - name: Noble AI, San Francisco, CA
   index: 1
date: 16 February 2020
bibliography: paper.bib

---


# Summary

``VlaPy`` is a 1-spatial-dimension, 1-velocity-dimension, Vlasov-Poisson-Fokker-Planck simulation code written in Python.  The Vlasov-Poisson-Fokker-Planck system of equations is commonly used in studying plasma physics in a variety of settings ranging from space physics to laboratory-created plasmas for fusion applications. 

The Vlasov-Poisson system is used to model collisionless plasmas. The Fokker-Planck operator is used to represent the effect of collisions. Rather than relying on numerical diffusion to smooth small-scale structures that inevitably arise when modeling collisionless plasmas, the Fokker-Planck equation enables a physical smoothing mechanism. 

The implementation here is based on finite-difference and pseudo-spectral methods. At the lowest level, ``VlaPy`` evolves a 2D grid in time according a set of coupled partial integro-differential equations over time. The dynamics are initialized through initial conditions or through an external force.

# Statement of Need

There is a plethora of software that solves the same equation set in academia [@Banks2017, @Joglekar2018], research labs, and industry, but a simple-to-read, open-source Python implementation is still lacking. This lack of simulation capability is echoed by the ``PlasmaPy`` [@plasmapy] community (``PlasmaPy`` is a collection of Open-Source plasma physics resources). ``VlaPy`` aims to fulfill these voids in the academic and research communities.

In general, ``VlaPy`` is designed to help students and researchers learn about concepts such as fundamental plasma physics and numerical methods as well as software-engineering-related topics such as unit and integrated testing, and extensible and maintainable code. The details of the implementation are provided in the following section. 


# Equations

The Vlasov-Poisson-Fokker-Planck system can be decomposed into 4 components. The normalized quantities are 
$\tilde{v} = v/v_{th}$, $\tilde{t} = t / \omega_p$, $\tilde{x} = x / (v_{th} / \omega_p)$, $\tilde{m} = m / m_e$, $\tilde{E} = e E / m_e$, $\tilde{f} = f / m n_e v_{th}^3$. The Fourier Transform operator is represented by $\mathcal{F}$. The subscript to the operator indicates the dimension of the transform. 

## Vlasov Equation

The normalized Vlasov equation is given by
$$ \frac{\partial f}{\partial t} + v  \frac{\partial f}{\partial x} + E \frac{\partial f}{\partial v} = 0 $$.

We use operator splitting to advance the time-step `@Cheng:1977`. Each one of those operators is then integrated pseudo-spectrally using the following methodology.

We first Fourier transform the operator like in 
$$ \mathcal{F}_x\left[ \frac{d f}{d t} = v \frac{d f}{d x} \right].$$
Then we solve for the change in the distribution function, discretize, and integrate, as given by
$$\frac{d\hat{f}}{\hat{f}} = v~ (-i k_x)~ dt, $$
$$ \hat{f}^{n+1}(k_x, v) = \exp(-i k_x ~ v \Delta t) ~~ \hat{f}^n(k_x, v). $$ 

The $E \partial f/\partial v$ term is stepped similarly using
$$ \hat{f}^{n+1}(x, k_v) = \exp(-i k_v ~ F \Delta t) ~~ \hat{f}^n(x, k_v) $$

We have implemented a simple Leapfrog scheme as well as a 4th order integrator called the 
Position-Extended-Forest-Ruth-Like Algorithm (PEFRL) [@Omelyan2002]

### Tests
The implementation of this equation is tested in the integrated tests section below.
