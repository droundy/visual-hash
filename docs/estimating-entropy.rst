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

If, however, we only change a fraction :math:`f` of the inputs
(i.e. random numbers) then the probability will be

.. math::
   P(f) = p^{f N}

Now if we measure this probability for a given :math:`f`, we are
unable to reconsttruct :math:`P(f=1)`, but if we measure this function
for a range of :math:`f`, then we can plot the log of :math:`P(f)`:

.. math::
   \log_2 P(f) = f N \log_2 p

which tells us that the resulting plot should be a straight line, and
its slope is :math:`\log_2 P(1)`.
