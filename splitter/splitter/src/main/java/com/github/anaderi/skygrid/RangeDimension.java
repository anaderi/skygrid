package com.github.anaderi.skygrid;

import java.util.ArrayList;
import java.util.List;


public class RangeDimension extends Dimension {
    private final int from_;
    private final int to_;
    public static final String TYPE_NAME = "RANGE";

    RangeDimension(int from, int to, String name) {
        super(to + 1 - from, name);
        from_ = from;
        to_ = to;
    }

    @Override
    public String description() {
        return RangeDimension.TYPE_NAME;
    }

    @Override
    public List<Dimension> split(List<Integer> proportion) {
        ArrayList<Dimension> result = new ArrayList<Dimension>(proportion.size());
        int i = from_;
        for (int pieceSize : proportion) {
            if (pieceSize == 0)
                continue;
            result.add(new RangeDimension(i, i + pieceSize - 1, name()));
            i += pieceSize;
        }
        assert i == to_ + 1;
        return result;
    }

    @Override
    public List<Integer> serialize() {
        ArrayList<Integer> result = new ArrayList<Integer>(2);
        result.add(from_);
        result.add(to_);
        return result;
    }

    @Override
    public boolean equals(Object o) {
        if (o instanceof RangeDimension) {
            RangeDimension d = (RangeDimension)o;
            return d.from_ == from_ && d.to_ == to_;
        }
        return false;
    }
}
