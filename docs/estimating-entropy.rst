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

Let us consider a system consisting of :math:`N` parts, each of which
has :math:`n` distinct configurations.  If I randomly modify one part,
then the chance of changing the system is :math:`q = 1 -
\frac{1}{n}`.  The entropy of such a system is given by

.. math::
   H = N \log_2 n

If I change a fraction :math:`f` of the parts of the system, the
probability of *not* changing the system is given by

.. math::
   P = (1 - fq)^N

Let us now consider a fraction :math:`f_a` that has a probability
:math:`a` of *not* changing the system.

.. math::
   a = (1 - f_a q)^N

We will assume that we can measure :math:`f_a`, and also that we can
(and do) measure :math:`f_{a^2}`, the fraction that leads to the
square of probability :math:`a`.

.. math::
   a^2 = (1 - f_{a^2} q)^N

We can solve for the following:

.. math::
   q = \frac{2f_a - f_{a^2}}{f_a^2}

.. math::
   N = \frac{\ln a}{\ln\left(\frac{f_{a^2}}{f_a} - 1\right)}

Taking these together, we can show that the entropy is given by

.. math::
   H = -\frac{\ln a}{\ln\left(\frac{f_{a^2}}{f_a} - 1\right)}
       \log_2 \left(1 - \frac{2f_a - f_{a^2}}{f_a^2}\right)

A nice option seems to be

.. math::
   a = \frac{\sqrt{5} - 1}{2}

.. math::
   a^2 = \frac{3 - \sqrt{5}}{2}

which balances the two at an average of 50%, thus avoiding a bias in
one direction or the other.  This is closely related to the golden
ratio.
