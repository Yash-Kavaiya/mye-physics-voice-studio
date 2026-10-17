# The Residue Theorem
> One number that solves impossible real integrals

## The Big Idea
? One number decides the integral | What if a whole contour integral depended on just one number per point?
Take a function that is analytic everywhere inside a closed loop, except at a few isolated poles.
Cauchy tells us the loop integral of an analytic function is zero. So all the action must come from the poles.
Near each pole, the Laurent series has a one over z minus a term. Its coefficient is called the residue.
$$ f(z)=\cdots+\frac{a_{-1}}{z-a}+a_0+a_1(z-a)+\cdots $$
Every other term integrates to zero around the loop. Only the residue survives, and it contributes two pi i times itself.
$$ \oint_C f(z)\,dz = 2\pi i\sum_k \operatorname{Res}_{z=a_k} f $$

## Computing Residues Fast
? No series needed | You rarely need the full Laurent series to find a residue.
For a simple pole, multiply by z minus a, then take the limit as z goes to a.
$$ \operatorname{Res}_{z=a} f=\lim_{z\to a}(z-a)f(z) $$
### Example: A simple pole
Find the residue of one over z squared plus one at z equals i.
$$ \operatorname{Res}_{z=i}\frac{1}{z^2+1}=\lim_{z\to i}\frac{1}{z+i}=\frac{1}{2i} $$

## A Real Integral
? Calculus gets stuck here | Here is a real integral that ordinary calculus finds hard, and residues make easy.
### Example: Exam-style problem
Evaluate the integral of one over one plus x squared, over the whole real line.
$$ I=\int_{-\infty}^{\infty}\frac{dx}{1+x^2} $$
Close the contour with a big semicircle in the upper half plane. Only the pole at z equals i lies inside.
The semicircle contributes nothing as the radius grows, so the integral equals two pi i times one over two i.
$$ I = 2\pi i\cdot\frac{1}{2i}=\pi $$
- Find the poles inside the contour
- Compute each residue
- Multiply the sum by two pi i
