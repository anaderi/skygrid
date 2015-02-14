package com.github.anaderi.skygrid;

import java.util.*;

/**
 * Scale is a separate field, despite of the fact that Scale
 * also is a class of Dimension hierarchy.
 * That is because splitting the cube by scale is very unefficient
 * and must be done only on the last step, when volume() == 1.
 * Because splitting the cube by the Scale-factor multiplies amount
 * of launches.
 */
public class Cube
{
    public static class ImpossibleToSplit extends Exception {}
    private final List<Dimension> dimensions_;
    private final Scale scale_;

    Cube(List<Dimension> dimensions, Scale scale) {
        dimensions_ = dimensions;
        scale_ = scale;
    }

    int volume() {
        int result = 1;
        for (Dimension dimension : dimensions_) {
            result *= dimension.length();
        }
        return result;
    }

    List<Dimension> dimensions() {
        return dimensions_;
    }
    Scale scale() {
        return scale_;
    }

    int selectBestSplitDimension(int splitCount) {
        int bestSplitDimensionIndex = -1;
        int bestSplitDisproportion = -1;
        int dimensionIndex = 0;
        for (Dimension dimension : dimensions_) {
            int disproportion = dimension.disproportion(splitCount);
            if (disproportion == 0)
                return dimensionIndex;
            int sliceVolume = volume() / dimension.length();
            if (bestSplitDisproportion == -1 ||
                    bestSplitDisproportion > sliceVolume) {
                bestSplitDisproportion = sliceVolume;
                bestSplitDimensionIndex = dimensionIndex;
            }
            ++dimensionIndex;
        }
        return bestSplitDimensionIndex;
    }

    public List<Cube> split(int splitCount) throws ImpossibleToSplit {
        return Cube.split(this, splitCount);
    }

    public int scaleFactor() {
        return scale_.length();
    }

    private static List<Cube> split(Cube parentCube, int splitCount) throws ImpossibleToSplit {
        assert splitCount > 0;
        Comparator<Cube> comparator = new CubeComparator();
        PriorityQueue<Cube> result = new PriorityQueue<Cube>(splitCount, comparator);
        result.add(parentCube);

        /**
         * It may happen that splitting a cube to e.g. 5 pieces cannot
         * be performed, because cube is 2x2. So we are to control cube's
         * "population" with this loop.
         *
         * As a result, volume of the biggest cube may be as much as 4-times
         * bigger than volume of the smallest, but not more.
         * Really, imagine that cube A bigger than B more than twice.
         * But B was created by splitting C to two quite equal pieces.
         * So, C = 2 * B, and C < A. So C cannot be chosen for splitting.
         */
        while (result.size() < splitCount) {
            Cube biggestCube = result.poll();
            if (biggestCube.volume() == 1) {
                if (biggestCube.scale_ == null)
                    throw new ImpossibleToSplit();
                List<Dimension> newScales = biggestCube.scale_.split(2);
                for (Dimension newScale : newScales) {
                    result.add(new Cube(biggestCube.dimensions_, (Scale) newScale));
                }
            } else {
                int bestDimensionToSplit = biggestCube.selectBestSplitDimension(2);
                List<Dimension> splittedDimensions =
                        biggestCube.dimensions_.get(bestDimensionToSplit).split(2);
                for (Dimension splitDimensionPart : splittedDimensions) {
                    List<Dimension> newDimensions = new ArrayList<Dimension>(biggestCube.dimensions_.size());
                    newDimensions.addAll(biggestCube.dimensions_.subList(0, bestDimensionToSplit));
                    newDimensions.add(splitDimensionPart);
                    newDimensions.addAll(
                            biggestCube.dimensions_.subList(
                                    bestDimensionToSplit + 1,
                                    biggestCube.dimensions_.size()));
                    result.add(new Cube(newDimensions, biggestCube.scale_));
                }
            }
        }
        return new ArrayList<Cube>(result);
    }

    private static class CubeComparator implements Comparator<Cube> {
        @Override
        public int compare(Cube o1, Cube o2) {
            boolean o1_has_no_scale = o1.scale_ == null;
            boolean o2_has_no_scale = o2.scale_ == null;
            assert (o1_has_no_scale == o2_has_no_scale);
            if (o1.volume() < o2.volume())
                return 1;
            if (o2.volume() < o1.volume())
                return -1;
            if (o1_has_no_scale)
                return 0;
            if (o1.scale_.length() < o2.scale_.length())
                return 1;
            if (o2.scale_.length() < o1.scale_.length())
                return -1;
            return 0;
        }
    }

    @Override
    public boolean equals(Object o) {
        if (o instanceof Cube) {
            Cube c = (Cube)o;
            return c.scale_.equals(scale_) &&
                    c.dimensions_.equals(dimensions_);
        }
        return false;
    }
}
