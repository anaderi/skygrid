package com.github.anaderi.skygrid;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

public class SetDimension extends Dimension {
    private final ArrayList<String> enums_;
    public static final String TYPE_NAME = "SET";

    SetDimension(Collection<String> enums) {
        super(enums.size());
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
            result.add(new SetDimension(enums_.subList(i, i + pieceSize)));
            i += pieceSize;
        }
        assert i == length();
        return result;
    }
}
