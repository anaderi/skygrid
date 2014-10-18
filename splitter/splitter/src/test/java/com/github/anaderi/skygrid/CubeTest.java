package com.github.anaderi.skygrid;

import junit.framework.TestCase;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class CubeTest extends TestCase {
    private Cube cube_;
    private static final int DEFAULT_SCALE = 1000;

    private void create2DimensionalCube(int sizeOne, int sizeTwo) {
        Scale scale = new Scale(DEFAULT_SCALE, "test");
        RangeDimension dimOne = new RangeDimension(1, sizeOne, "test");
        RangeDimension dimTwo = new RangeDimension(1, sizeTwo, "test");
        ArrayList<Dimension> dimensions = new ArrayList<Dimension>(2);
        dimensions.add(dimOne);
        dimensions.add(dimTwo);
        cube_ = new Cube(dimensions, scale);
    }

    private void create3DimensionalCube(int sizeOne, int sizeTwo, int sizeThree) {
        Scale scale = new Scale(DEFAULT_SCALE, "test");
        RangeDimension dimOne = new RangeDimension(1, sizeOne, "test");
        RangeDimension dimTwo = new RangeDimension(1, sizeTwo, "test");
        RangeDimension dimThree = new RangeDimension(1, sizeThree, "test");
        ArrayList<Dimension> dimensions = new ArrayList<Dimension>(3);
        dimensions.add(dimOne);
        dimensions.add(dimTwo);
        dimensions.add(dimThree);
        cube_ = new Cube(dimensions, scale);
    }

    public void testVolume() {
        create2DimensionalCube(4, 9);
        assertEquals(36, cube_.volume());
    }

    public void testDimensionSelection_First() {
        // First dimension has length == 4, so split it.
        create2DimensionalCube(4, 9);
        assertEquals(0, cube_.selectBestSplitDimension(2));
    }

    public void testDimensionSelection_Second() {
        // Second dimension has length == 9, so split it.
        create2DimensionalCube(4, 9);
        assertEquals(1, cube_.selectBestSplitDimension(3));
    }

    public void testDimensionSelection_Third() {
        /**
         * First dimension has length == 4, so after split there will be
         * 4 slices with size 9. So, disproportion is 9.
         *
         * Second dimension has length == 9, so after split there will be
         * 5 slices with sizes 2, 2, 2, 2, 1, and volumes 8, 8, 8, 8, 4.
         * So disproportion will be 4.
         *
         * Select second.
         */
        create2DimensionalCube(4, 9);
        assertEquals(1, cube_.selectBestSplitDimension(5));
    }

    public void testDimensionSelect_Fourth() {
        create3DimensionalCube(2, 4, 3);
        assertEquals(1, cube_.selectBestSplitDimension(15));
    }

    public void testDimensionSelection_Auto() {
        for (int firstSize = 1; firstSize < 100; ++firstSize) {
            for (int secondSize = 1; secondSize < 100; ++secondSize) {
                create2DimensionalCube(firstSize, secondSize);
                int selectedDimension = cube_.selectBestSplitDimension(2);
                int volumeDifference = selectedDimension == 0 ?
                        (firstSize % 2) * secondSize :
                        (secondSize % 2) * firstSize;
                int minimalDifference = cube_.volume();

                // Try every split by first dimension.
                for (int splitPosition = 0; splitPosition <= firstSize; ++splitPosition) {
                    int currentDifference = Math.abs(
                            splitPosition - (firstSize - splitPosition)) * secondSize;
                    if (minimalDifference > currentDifference)
                        minimalDifference = currentDifference;
                }

                // Try every split by second dimension.
                for (int splitPosition = 0; splitPosition <= secondSize; ++splitPosition) {
                    int currentDifference = Math.abs(
                            splitPosition - (secondSize - splitPosition)) * firstSize;
                    if (minimalDifference > currentDifference)
                        minimalDifference = currentDifference;
                }

                assertEquals(minimalDifference, volumeDifference);
            }
        }
    }

    public void testSplit_One() throws Cube.ImpossibleToSplit {
        create3DimensionalCube(2, 2, 2);
        List<Cube> result = cube_.split(1);
        assertEquals(1, result.size());
        assertEquals(8, result.get(0).volume());
        assertEquals(1000, result.get(0).scaleFactor());
    }

    public void testSplit_Two() throws Cube.ImpossibleToSplit {
        create3DimensionalCube(2, 2, 2);
        List<Cube> result = cube_.split(4);
        assertEquals(4, result.size());
        for (Cube slice : result) {
            assertEquals(2, slice.volume());
            assertEquals(1000, slice.scaleFactor());
        }
    }

    public void testSplit_Three() throws Cube.ImpossibleToSplit {
        create3DimensionalCube(2, 2, 2);
        List<Cube> result = cube_.split(16);
        assertEquals(16, result.size());
        for (Cube slice : result) {
            assertEquals(1, slice.volume());
            assertEquals(500, slice.scaleFactor());
        }
    }

    public void testSplit_Four() throws Cube.ImpossibleToSplit {
        create2DimensionalCube(1, 1);
        List<Cube> result = cube_.split(4);
        assertEquals(4, result.size());
        for (Cube slice : result) {
            assertEquals(1, slice.volume());
            assertEquals(250, slice.scaleFactor());
        }
    }

    public void testSplit_noScale() throws Cube.ImpossibleToSplit {
        RangeDimension dimOne = new RangeDimension(1, 4, "test");
        RangeDimension dimTwo = new RangeDimension(1, 4, "test");
        ArrayList<Dimension> dimensions = new ArrayList<Dimension>(2);
        dimensions.add(dimOne);
        dimensions.add(dimTwo);
        cube_ = new Cube(dimensions, null);
        List<Cube> cubes = cube_.split(4);
        assertEquals(4, cubes.size());
    }

    public void testSplit_noScaleImpossible() throws Cube.ImpossibleToSplit {
        RangeDimension dimOne = new RangeDimension(1, 2, "test");
        RangeDimension dimTwo = new RangeDimension(1, 2, "test");
        ArrayList<Dimension> dimensions = new ArrayList<Dimension>(2);
        dimensions.add(dimOne);
        dimensions.add(dimTwo);
        cube_ = new Cube(dimensions, null);
        boolean wasException = false;
        try {
            cube_.split(16);
        } catch (Cube.ImpossibleToSplit e) {
            wasException = true;
        }
        assertTrue(wasException);
    }

    public void testSplit_Auto() throws Cube.ImpossibleToSplit {
        float maxDisbalance = -1;
        for (int firstDimension = 1; firstDimension < 5; ++firstDimension) {
            for (int secondDimension = 1; secondDimension < 5; ++secondDimension) {
                for (int thirdDimension = 1; thirdDimension < 5; ++thirdDimension) {
                    create3DimensionalCube(firstDimension, secondDimension, thirdDimension);
                    for (int splitCount = 1;
                         splitCount < 7 * firstDimension * secondDimension * thirdDimension;
                         ++splitCount) {
                        List<Cube> result = cube_.split(splitCount);
                        assertEquals(splitCount, result.size());
                        int maxCubeVolume = -1;
                        int minCubeVolume = -1;
                        int totalVolume = 0;
                        for (Cube subCube : result) {
                            int cubeTotalVolume = subCube.volume() * subCube.scaleFactor();
                            if (maxCubeVolume == -1 || maxCubeVolume < cubeTotalVolume)
                                maxCubeVolume = cubeTotalVolume;
                            if (minCubeVolume == -1 || minCubeVolume > cubeTotalVolume)
                                minCubeVolume = cubeTotalVolume;
                            totalVolume += cubeTotalVolume;
                        }
                        assertEquals(firstDimension * secondDimension * thirdDimension * DEFAULT_SCALE,
                                     totalVolume);
                        float difference = maxCubeVolume / minCubeVolume;
                        if (maxDisbalance == -1 || difference > maxDisbalance)
                            maxDisbalance = difference;
                    }
                }
            }
        }
        assertTrue(maxDisbalance <= 4.0f);
    }
}
