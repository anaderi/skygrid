package com.github.anaderi.skygrid;

import java.util.ArrayList;
import java.util.List;

public class Scale extends Dimension {
    private final int volume_;

    Scale(int volume) {
        super(volume);
        volume_ = volume;
    }

    @Override
    public String description() {
        return "SCALE";
    }

    @Override
    public List<Dimension> split(List<Integer> proportion) {
        List<Dimension> result = new ArrayList<Dimension>(proportion.size());
        int totalVolume = 0;
        for (Integer volume : proportion) {
            totalVolume += volume;
            result.add(new Scale(volume));
        }
        assert volume_ == totalVolume;
        return result;
    }
}
