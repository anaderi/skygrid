package com.github.anaderi.skygrid;

import junit.framework.TestCase;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;

public class DimensionTest extends TestCase {
    private class MockDimension extends Dimension {
        public MockDimension(Integer size) { super(size, "test"); }

        @Override
        public String description() {
            return null;
        }

        @Override
        public List<Dimension> split(List<Integer> proportion) {
            return null;
        }

        @Override
        public List<Integer> serialize() {
            return null;
        }
    }

    public void testSplitOne() {
        Dimension d = new MockDimension(1);
        assertEquals(0, d.disproportion(1));
        assertEquals(1, d.disproportion(2));
        assertEquals(4, d.disproportion(5));
        assertEquals(18, d.disproportion(19));
    }

    public void testSplitSeven() {
        Dimension d = new MockDimension(7);
        assertEquals(0, d.disproportion(1));
        assertEquals(1, d.disproportion(2));  // 3 + 4
        assertEquals(1, d.disproportion(5));  // 1 + 1 + 1 + 2 + 2
        assertEquals(0, d.disproportion(7));
        assertEquals(94, d.disproportion(101));
    }

    public void testSplitEight() {
        Dimension d = new MockDimension(8);
        assertEquals(0, d.disproportion(1));
        assertEquals(1, d.disproportion(3));  // 2 + 3 + 3
        assertEquals(1, d.disproportion(5));  // 1 + 1 + 2 + 2 + 2
        assertEquals(1, d.disproportion(7));  // 1 + 1 + 1 + 1 + 1 + 1 + 2
        assertEquals(93, d.disproportion(101));
    }

    public void testSplitFourteen() {
        Dimension d = new MockDimension(14);
        assertEquals(0, d.disproportion(1));  // 14
        assertEquals(0, d.disproportion(2));  // 7 + 7
        assertEquals(1, d.disproportion(3));  // 4 + 5 + 5
        assertEquals(1, d.disproportion(5));  // 2 + 3 + 3 + 3 + 3
        assertEquals(87, d.disproportion(101));
    }

    public void testSplitToOnePiece() {
        for (int size = 1; size < 10; ++size) {
            Dimension d = new MockDimension(size);
            List<Integer> pieces = d.calculateSplitProportion(1);
            assertEquals(1, pieces.size());
            assertEquals(size, (int)pieces.get(0));
        }
    }

    public void testSplitProportionOne() {
        Dimension d = new MockDimension(1);
        Integer[] canonResult = {1, 0, 0, 0};
        assertEquals(Arrays.asList(canonResult),
                     d.calculateSplitProportion(4));
    }

    public void testSplitProportionFour() {
        Dimension d = new MockDimension(4);
        Integer[] canonResult = {1, 1, 1, 1, 0, 0, 0, 0};
        assertEquals(Arrays.asList(canonResult),
                d.calculateSplitProportion(8));
    }

    public void testSplitProportionEleven() {
        Dimension d = new MockDimension(11);
        Integer[] canonResult = {4, 4, 3};
        assertEquals(Arrays.asList(canonResult),
                d.calculateSplitProportion(3));
    }

    public void testSplitProportionStress() {
        for (int dimensionSize = 1; dimensionSize < 101; ++dimensionSize) {
            for (int splitSize = 1; splitSize < 101; ++splitSize) {
                Dimension d = new MockDimension(dimensionSize);
                List<Integer> splits = d.calculateSplitProportion(splitSize);
                assertEquals(splitSize, splits.size());
                HashSet<Integer> sizes = new HashSet<Integer>();
                int totalSize = 0;
                for (Integer currentSplitSize : splits) {
                    totalSize += currentSplitSize;
                    sizes.add(currentSplitSize);
                }
                assertEquals(dimensionSize, totalSize);
                assertTrue(sizes.size() == 1 || sizes.size() == 2);
                if (sizes.size() == 2) {
                    Iterator<Integer> sizesIterator = sizes.iterator();
                    Integer firstSize = sizesIterator.next();
                    Integer secondSize = sizesIterator.next();
                    assertEquals(1, Math.abs(firstSize - secondSize));
                }
            }
        }
    }
}