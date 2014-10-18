package com.github.anaderi.skygrid;

import junit.framework.TestCase;

import java.util.Arrays;
import java.util.List;

public class RangeDimensionTest extends TestCase {
    private final Dimension originalDimension_ = new RangeDimension(100, 102, "test");

    public void testDimensionSize() {
        assertEquals(3, originalDimension_.length());  // 100, 101, 102
    }

    public void testDimensionDivision() {
        List<Dimension> split = originalDimension_.split(2);
        assertEquals(RangeDimension.class, split.get(0).getClass());
        assertEquals(RangeDimension.class, split.get(1).getClass());
        assertEquals(2, split.get(0).length());
        assertEquals(1, split.get(1).length());
    }

    public void testDimensionDivisionWithWrongSize() {
        boolean wasExceptionThrown = false;
        try {
            Integer[] splits = {1, 2, 3, 4};
            originalDimension_.split(Arrays.asList(splits));
        } catch (AssertionError e) {
            wasExceptionThrown = true;
        }
        assertTrue(wasExceptionThrown);
    }
}
