package com.github.anaderi.skygrid;

import java.util.ArrayList;
import java.util.List;

public abstract class Dimension {
    private final int length_;
    private final String name_;

    Dimension(int length, String name) {
        length_ = length;
        name_ = name;
    }

    public abstract String description();
    public abstract List<Dimension> split(List<Integer> proportion);
    public abstract List<Integer> serialize();

    public int length() {
        return length_;
    }

    public String name() {
        return name_;
    }

    /**
     * Returns amount of slices in difference between the most
     * full and the most empty pieces.
     */
    public int disproportion(int splitCount) {
        if (splitCount >= length_) {
            // Some parts will get a task, and others will not.
            // In this case disproportion is not 1, it is very large.
            return splitCount - length_;
        }

        return (length_ % splitCount == 0 ? 0 : 1);
    }

    /**
     * Calculates a proportion in which the dimension should be split.
     */
    public List<Integer> calculateSplitProportion(int splitCount) {
        int minimalAmount = length() / splitCount;
        int extraAmonut = minimalAmount + 1;
        int amountOfElementsWithExtraSlices = length() % splitCount;
        int i = 0;
        ArrayList<Integer> result = new ArrayList<Integer>(splitCount);
        for (; i < amountOfElementsWithExtraSlices; ++i) {
            result.add(extraAmonut);
        }
        for (; i < splitCount; ++i) {
            result.add(minimalAmount);
        }
        return result;
    }

    public List<Dimension> split(int splitCount) {
        return split(calculateSplitProportion(splitCount));
    }
}
