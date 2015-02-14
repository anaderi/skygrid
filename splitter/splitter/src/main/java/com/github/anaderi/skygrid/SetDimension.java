package com.github.anaderi.skygrid;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

public class SetDimension extends Dimension {
    private final ArrayList<String> enums_;
    public static final String TYPE_NAME = "SET";

    SetDimension(Collection<String> enums, String name) {
        super(enums.size(), name);
        enums_ = new ArrayList<String>(enums);
    }

    @Override
    public String description() {
        return SetDimension.TYPE_NAME;
    }

    @Override
    public List<Dimension> split(List<Integer> proportion) {
        ArrayList<Dimension> result = new ArrayList<Dimension>(proportion.size());
        int i = 0;
        for (int pieceSize : proportion) {
            if (pieceSize == 0)
                continue;
            result.add(new SetDimension(enums_.subList(i, i + pieceSize), name()));
            i += pieceSize;
        }
        assert i == length();
        return result;
    }

    @Override
    public List<Integer> serialize() {
        ArrayList<Integer> result = new ArrayList<Integer>(enums_.size());
        for (String value : enums_) {
            result.add(Integer.valueOf(value));
        }
        return result;
    }

    @Override
    public boolean equals(Object o) {
        if (o instanceof SetDimension) {
            SetDimension d = (SetDimension)o;
            return d.enums_.equals(enums_);
        }
        return false;
    }
}
