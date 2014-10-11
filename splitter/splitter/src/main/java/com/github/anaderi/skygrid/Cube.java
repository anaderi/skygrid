package com.github.anaderi.skygrid;

import java.util.List;

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
}
