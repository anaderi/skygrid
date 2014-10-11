package com.github.anaderi.skygrid;

import junit.framework.TestCase;

import java.util.Arrays;
import java.util.List;

public class ScaleTest extends TestCase {
    public void testScaleGeneration() {
        Dimension d = new Scale(1000);
        List<Dimension> slices = d.split(3);
        assertEquals(3, slices.size());
        assertEquals(Scale.class, slices.get(0).getClass());
        assertEquals(Scale.class, slices.get(1).getClass());
        assertEquals(Scale.class, slices.get(2).getClass());
        assertEquals(334, slices.get(0).length());
        assertEquals(333, slices.get(1).length());
        assertEquals(333, slices.get(2).length());
    }

    public void testScaleInternalCheck() {
        Dimension d = new Scale(1000);
        Integer[] sliceSizes = {300, 400, 500};
        boolean wasExceptionThrown = false;
        try {
            d.split(Arrays.asList(sliceSizes));
        } catch (AssertionError e) {
            wasExceptionThrown = true;
        }
        assertTrue(wasExceptionThrown);
    }
}
