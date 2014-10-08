package com.github.anaderi.skygrid;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

/**
 * Created by stromsund on 05.10.14.
 */
public class SetDimension extends Dimension {
    private final ArrayList<String> enums_;

    SetDimension(Collection<String> enums) {
        super(enums.size());
        enums_ = new ArrayList<String>(enums);
    }

    public String description() {
        return "SET";
    }

    public List<Dimension> split(List<Integer> proportion) { return null; }
}
