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

Estimating the entropy take II
------------------------------

Let us consider a system consisting of :math:`N` parts, each of which
has :math:`n` distinct configurations.  If I randomly modify one part,
then the chance of changing the system is :math:`q = 1 -
\frac{1}{n}`.  The entropy of such a system is given by

.. math::
   H = N \log_2 n

If I change a fraction :math:`f` of the parts of the system, the
probability of changing the system is given by

.. math::
   P = 1 - (fq)^N

where :math:`q` is the probability of a given thing *not* changing the
system when it is modified.
Let us now consider a fraction :math:`f_\gamma` that has a probability
:math:`\gamma` of *not* changing the system.

.. math::
   \gamma = (f_\gamma q)^N

We will assume that we can measure :math:`f_\gamma`, and also that we can
(and do) measure :math:`f_{\gamma^2}`, the fraction that leads to the
square of probability :math:`\gamma`.

.. math::
   \gamma^2 = (f_{\gamma^2} q)^N

We can solve for the following:

.. math::
   q = \frac{f_{\gamma^2}}{f_\gamma^2} = 1/n

.. math::
   N = \frac{\ln \gamma}{\ln\left(f_\gamma q\right)}

.. math::
   N = \frac{\ln \gamma}{\ln\left(\frac{f_{\gamma^2}}{f_\gamma} \right)}

Taking these together, we can show that the entropy is given by

.. math::
   H = \frac{\ln \gamma}{\ln\left(\frac{f_{\gamma^2}}{f_\gamma}
   \right)}
       \log_2 \left(\frac{f_\gamma^2}{f_{\gamma^2}}\right)

A nice option seems to be

.. math::
   \gamma = \frac{\sqrt{5} - 1}{2}

.. math::
   \gamma^2 = \frac{3 - \sqrt{5}}{2}

which balances the two at an average of 50%, thus avoiding a bias in
one direction or the other.  This is the golden ratio minus one.
