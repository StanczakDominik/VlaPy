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
 - name: Noble.AI, 8 California St, Suite 400, San Francisco, California 94111
   index: 1
date: 16 February 2020
bibliography: paper.bib

---

# Summary

Here we introduce ``VlaPy``: a 1-spatial-dimension, 1-velocity-dimension, Eulerian Vlasov-Poisson-Fokker-Planck simulation code written in Python.  

The Vlasov-Poisson-Fokker-Planck system of equations is commonly used to study plasma and fluid physics in a broad set of topical environments, ranging from space physics, to laboratory-created plasmas for fusion applications (see refs. [@Betti2016; @Fasoli2016; @Ongena2016; @Chen2019]). More specifically, the Vlasov-Poisson system of equations is typically employed to model collisionless plasmas. The Fokker-Planck operator can be introduced into this system to represent the effect of collisions. The primary advantage of this scheme is that instead of relying on numerical diffusion to smooth small-scale structures that arise when modeling collisionless plasmas, the Fokker-Planck operator enables a physics-based smoothing mechanism. 

Our implementation is based on finite-difference and pseudo-spectral methods. At the lowest level, ``VlaPy`` evolves a two-dimensional (2D) grid according to this set of coupled partial integro-differential equations over time. In ``VlaPy``, the simulation dynamics can be initialized through user-specified initial conditions or external forces.

# Statement of Need

There are many software libraries that solve the same equation set which are available in academic settings, research laboratories, and industry (e.g., [@Banks2017; @Joglekar2018]), but the community has yet to benefit from a simple-to-read, open-source Python implementation. This lack of capability is currently echoed in conversations within the ``PlasmaPy`` [@plasmapy] community (``PlasmaPy`` is a collection of open-source plasma physics resources). Our aim with ``VlaPy`` is to take a step towards filling this need in the open-source community.

``VlaPy`` is intended to help students and researchers learn about and explore concepts in fundamental plasma and fluid physics and numerical methods.  It is also designed to provide a science-accessible introduction to industry and software engineering best-practices, including unit and integrated testing, and extensible and maintainable code. 

The details of the ``VlaPy`` implementation are provided in the following sections. 


# Equations

The Vlasov-Poisson-Fokker-Planck system can be decomposed into 4 components. These components, represented using normalized units, are 
$\tilde{v} = v/v_{th}$, $\tilde{t} = t / \omega_p$, $\tilde{x} = x / (v_{th} / \omega_p)$, $\tilde{m} = m / m_e$, $\tilde{E} = e E / m_e$, $\tilde{f} = f / m n_e v_{th}^3$. The Fourier transform operator is represented by $\mathcal{F}$ and the subscript to the operator indicates the dimension of the transform. 

The Vlasov-Poisson-Fokker-Planck system can be decomposed into 4 components. The normalized quantities are 
$\tilde{v} = v/v_{th}$, $\tilde{t} = t / \omega_p$, $\tilde{x} = x / (v_{th} / \omega_p)$, $\tilde{m} = m / m_e$, $\tilde{E} = e E / m_e$, $\tilde{f} = f / m n_e v_{th}^3$. The Fourier Transform operator is represented by $\mathcal{F}$. The subscript to the operator indicates the dimension of the transform. 

## Vlasov Equation

The normalized Vlasov equation is given by
$$ \frac{\partial f}{\partial t} + v  \frac{\partial f}{\partial x} + E \frac{\partial f}{\partial v} = 0 $$.

We use operator splitting to advance the time-step `@Cheng:1977`. Each one of those operators is then integrated pseudo-spectrally using the following methodology.

We first Fourier transform the operator, as given by 
$$ \mathcal{F}_x\left[ \frac{d f}{d t} = v \frac{d f}{d x} \right].$$

Next, we solve for the change in the plasma distribution function, discretize, and integrate, as given by
$$\frac{d\hat{f}}{\hat{f}} = v~ (-i k_x)~ dt, $$
$$ \hat{f}^{n+1}(k_x, v) = \exp(-i k_x ~ v \Delta t) ~~ \hat{f}^n(k_x, v). $$ 

The $E \partial f/\partial v$ term is evolved similarly using
$$ \hat{f}^{n+1}(x, k_v) = \exp(-i k_v ~ F \Delta t) ~~ \hat{f}^n(x, k_v) $$

We have implemented a simple Leapfrog scheme as well as a 4th order integrator called the 
Position-Extended-Forest-Ruth-Like Algorithm (PEFRL) [@Omelyan2002]

### Tests
The implementation of this equation is tested in the integrated tests section below.

## Poisson Equation

The normalized Poisson equation is simply
$$  \nabla^2 \Phi = \rho $$

Because the ion species are effectively static and form a charge-neutralizing background to the electron dynamics, we can express the Poisson equation as
$$ - \nabla E = \rho_{net} = 1 - \rho_e $$ 

This is justifed by the assumption that the relevant time-scales are short compared to the time-scale associated to ion motion.

In 1 spatial dimension, this can be expressed as

$$ - \frac{d}{dx} E(x) = 1 - \int f(x,v) ~dv $$

and the discretized version that is solved is

$$  E(x_i)^{n+1} = \mathcal{F}_x^{-1}\left[\frac{\sum_j f(x_i,v_j)^n \Delta v}{- i k_x}\right] $$

### Integrated Code Testing
Unit tests are provided for this operator to validate its performance and operation under the above assumptions.  These are simply unit tests against analytical solutions of integrals of periodic functions.


## Fokker-Planck Equation

We use a simplified version of the full Fokker-Planck operator [@Lenard1958]. This is given by

$$\left(\frac{\delta f}{\delta t}\right)_{\text{coll}} = \nu \frac{\partial}{\partial v} \left ( v f + v_0^2 \frac{\partial f}{\partial v}\right), $$
where $v_0$ is the thermal velocity associated with the Maxwell-Boltzmann distribution that is a solution to this equation.

We discretize this backward-in-time, centered-in-space. This procedure results in the time-step scheme given by
$$ f^{n} = {\Delta t} \nu \left[\left(-\frac{v_0^2}{\Delta v^2} + \frac{1}{2\Delta v}\right) v_{j+1}f^{n+1}_{j+1} + \left(1+2\frac{v_0^2}{\Delta v^2}\right) f^{n+1}_j + \left(-\frac{v_0^2}{\Delta v^2} - \frac{1}{2\Delta v}\right) v_{j-1}f^{n+1}_{j-1}  \right]. $$ 

This forms a tridiagonal system of equations that can be directly inverted.

### Integrated Code Testing
Unit tests are provided for this operator. The unit tests ensure that

1. The operator conserves number density.


2. The operator reverts to a solution with a temperature proportional to $v_0^2$.


3. The operator does not impact a Maxwell-Boltzmann distribution already satisfying $v_{th} = v_0$.


4. The operator acts to evolve the distribution to a mean velocity of $0$ if initialized with an off-center drift velocity.

# Integrated Code Tests against Plasma Physics: Electron Plasma Waves and Landau Damping

One of the most fundamental plasma physics phenomenon is known as Landau Damping. An extensive review is provided in ref. [@Ryutov1999].  

Plasmas can support electrostatic oscillations. The oscillation frequency is given by the electrostatic electron plasma wave (EPW) dispersion relation. When a wave of sufficiently small amplitude is driven at the resonant wave-number and frequency pairing, there is a resonant exchange of energy between the plasma and the electric field, and the electrons can damp the electric field. The damping rates, as well as the resonant frequencies, are given in ref. [@Canosa1973].

In the ``VlaPy`` simulation code, we have verified that the known damping rates for Landau Damping are reproduced, for a few different wave-numbers. This is shown in `notebooks/landau_damping.ipynb`. 

We include validation against this phenomenon as an integrated test.

# Acknowledgements
We use xarray [@Hoyer2017] for file storage and MLFlow [@Zaharia2018] for experiment management.

We acknowledge valuable discussions with Pierre Navarro on the implementation of the Vlasov equation.

# References
