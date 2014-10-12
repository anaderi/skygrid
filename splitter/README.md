Splitter
========

Splitter is a Java library, that splits a N-dimensional cube of tasks
into exactly M quite equal pieces. Split can be performed only along some direction,
so, the result of split is also a set of N-dimensional cubes.

Sum of volumes of that cubes is equal to the original cube volume.

Split algorithm after a countable amount of repetitions with random numbers had
the following distribution of disbalance between the biggest and the smallest
cubes:

    {1.0=6884, 2.0=603669, 3.0=26593}
