package com.github.anaderi.skygrid;

import junit.framework.TestCase;

import java.util.Arrays;
import java.util.List;

public class SetDimensionTest extends TestCase {
    private final String[] SET_DATA = {"Robin", "Bobin", "Barabek"};
    private final SetDimension originalDimension_ = new SetDimension(Arrays.asList(SET_DATA));

    private void checkSingleSplit(List<Dimension> splitResult) {
        assertEquals(1, splitResult.size());
        assertEquals(SetDimension.class, splitResult.get(0).getClass());
        assertEquals(3, splitResult.get(0).length());
    }

    private void checkDoubleSplit(List<Dimension> splitResult) {
        assertEquals(2, splitResult.size());
        assertEquals(SetDimension.class, splitResult.get(0).getClass());
        assertEquals(SetDimension.class, splitResult.get(1).getClass());
        assertTrue(1 == splitResult.get(0).length() && 2 == splitResult.get(1).length() ||
                   2 == splitResult.get(0).length() && 1 == splitResult.get(1).length());
    }

    private List<Dimension> getSplitResult(Integer[] proportions) {
        return originalDimension_.split(Arrays.asList(proportions));
    }

    public void testDividingASetManuallyOne() {
        Integer[] proportions = {3};
        List<Dimension> splitResult = getSplitResult(proportions);
        checkSingleSplit(splitResult);
    }

    public void testDividingASetManuallyTwo() {
        Integer[] proportions = {1, 2};
        List<Dimension> splitResult = getSplitResult(proportions);
        checkDoubleSplit(splitResult);
    }

    public void testDividingASetManuallyZero() {
        Integer[] proportions = {0, 3, 0, 0};
        List<Dimension> splitResult = getSplitResult(proportions);
        checkSingleSplit(splitResult);
    }

    public void testDividingASetManuallyException() {
        boolean wasExceptionThrown = false;
        try {
            Integer[] proportions = {0, 1, 0, 0};
            getSplitResult(proportions);
        } catch (AssertionError e) {
            wasExceptionThrown = true;
        }
        assertTrue(wasExceptionThrown);
    }

    public void testDividingAutomaticallyOne() {
        List<Dimension> splitResult = originalDimension_.split(1);
        checkSingleSplit(splitResult);
    }

    public void testDividingAutomaticallyTwo() {
        List<Dimension> splitResult = originalDimension_.split(2);
        checkDoubleSplit(splitResult);
    }
}
