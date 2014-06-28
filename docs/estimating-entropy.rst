Estimating Entropy
==================

We are interested in the amount of entropy (or information) that is
transferred to humans in a visual hash.  It is worth taking a moment
to define terms in a human-centric manner.

Self-information
----------------

The **self-information** of a given image is given by

.. math::
   I(x) = -\log_2 P(x)

where :math:`P(x)` is the probability of observing state :math:`x`.

Information
-----------

The **information** (or entropy) of a system is actually the weighted
average of the self-information all possible states.

.. math::
   H = -\sum_{x} P(x)\log_2 P(x)

Estimating the entropy
----------------------

To estimate the entropy, we need to make some assumptions.  We assume
that the visual hash is distinguishable if any of :math:`N` inputs
changes independently.  We further assume that each of these changes
has probability :math:`p`.  Thus the probability of an
indistinguishable state showing up when we generate a new hash is
given by

.. math::
   P = p^N
   :label: P

If, however, we only change a fraction :math:`f` of the inputs
(i.e. random numbers) then the probability will be

.. math::
   P(f) = \left(1 - f(1 - p)\right)^N

   = \left(1 - f + fp\right)^N

This comes from the probability :math:`f(1-p)` that the image will
change due to a single number changing.  Since any one of :math:`N`
numbers could change in this way, the probability of the image *not*
changing is as specified in the formula above.  Note that if
:math:`f=1` this formula reduces to equation :eq:`P`.

Now if we measure this probability for a given :math:`f`, we are
unable to reconsttruct :math:`P(f=1)`, but if we measure this function
for a range of :math:`f`, then we should be able to extract both
:math:`p` and :math:`N`.

If we consider the limit of :math:`f\ll 1`, we can keep just the first
term in a power series expansion.

.. math::
   P(f) = 1 - Nf(1-p) + \frac{N(N-1)f^2(1-p)^2}{2} + \mathcal{O}(f^3)

Thus, if we can measure the first two derivatives of :math:`P(f)`, we
could in principle measure :math:`N` and :math:`1-p` separately.  But
that seems dubious, since :math:`N` is likely a large number, so
:math:`N(N-1) \approx N^2`, which would make the first and second
derivatives of :math:`P(f)` redundant.

Another measure we could use is the "half-way" point
:math:`f_{\frac12}`, defined by:

.. math::
   P(f_{\frac12}) = \frac12 = \left(1 - f_{\frac12}(1 - p)\right)^N

Solving this equation, we find that:

.. math::
   f_{\frac12} = \frac{1 - 2^{-\frac1N}}{1-p}

Combining this with the initial slope

.. math::
   f_0' = -N(1-p),

we find that

.. math::
   f_0' f_{\frac12} = -N\left( 1 - 2^{-\frac1N}\right)

which is a nonlinear equation we can solve numerically.
Incidentally, in the limit that :math:`N \gg 1`, it is approximately
true that

.. math::
   2^{-\frac1N} \approx 1 - \frac{\ln 2}{N} + \frac12 \frac{\ln 2 ^2}{N^2},

and we can conclude that

.. math::
   f_0' f_{\frac12} \approx -N\left(1 -1 + \frac{\ln 2}{N} - \frac{\ln 2 ^2}{2N^2}\right)
   \\
   = -\ln 2 + \frac{\ln 2^2}{2N}

.. math::
   N \approx \frac{\ln 2^2}{2 f_0' f_{\frac12} + 2\ln 2}
   :label: N approx

.. math::
   1 - p \approx -f_0'\frac{2 f_0' f_{\frac12} + 2\ln 2}{\ln 2^2}

   p \approx 1 + f_0'\frac{2 f_0' f_{\frac12} + 2\ln 2}{\ln 2^2}

which means we can conclude that

.. math::
   P \approx \left(1 + f_0'\frac{2 f_0' f_{\frac12} + 2\ln 2}{\ln
   2^2}\right)
   ^{\frac{\ln 2^2}{2 f_0' f_{\frac12} + 2\ln 2}}

Numerically, we can arrive at a better solution than this, but it
seems good to have a simple analytic understanding of how our answer
will work out.  We can naturally check this approximation by
evaluating equation :eq:`N approx` for :math:`N` to verify that it is
large.

Estimating the entropy take II
------------------------------

If we use a probabilistic bisection algorithm, we should be able to
pretty easily measure the :math:`f` that leads to
:math:`P(f_{\frac23})=\frac23` and :math:`P(f_{\frac13})=\frac13` (or
any other pair of fractions).  Given these two numbers, we should be
able to solve for :math:`p` and :math:`N` above.

.. math::
   P(f_{\frac13}) = \frac13 = \left(1 - f_{\frac13}(1 - p)\right)^N

.. math::
   P(f_{\frac23}) = \frac23 = \left(1 - f_{\frac23}(1 - p)\right)^N

.. math::
   -\ln 3 = N \ln\left(1 - f_{\frac13}(1 - p)\right)

.. math::
   \ln 2 -\ln 3 = N \ln\left(1 - f_{\frac23}(1 - p)\right)

.. math::
   \frac{\ln 3}{\ln 3 - \ln 2} = \frac{\ln\left(1 - f_{\frac13}(1 - p)\right)}{\ln\left(1 - f_{\frac23}(1 - p)\right)}

.. math::
   \frac{\ln 3}{\ln 3 - \ln 2} \ln\left(1 - f_{\frac23}(1 - p)\right)
   =
   \ln\left(1 - f_{\frac13}(1 - p)\right)



