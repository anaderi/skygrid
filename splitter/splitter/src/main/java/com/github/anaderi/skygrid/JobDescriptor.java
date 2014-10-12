package com.github.anaderi.skygrid;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;

import java.io.IOException;
import java.util.ArrayList;

/**
 * This class implements JobDescriptor
 * https://github.com/anaderi/skygrid/wiki/Job-descriptor
 */
public class JobDescriptor {
    private static final String ARGS = "args";
    private static final String SCALE_ARGS = "scaleArg";

    private Cube argsCube_;
    private JsonNode root_;

    public static class UnknownDimensionType extends Exception {}

    JobDescriptor(Cube argsCube, JsonNode root) {
        argsCube_ = argsCube;
        root_ = root;
    }

    public static JobDescriptor fromJsonString(String input) throws UnknownDimensionType, IOException {
        ObjectMapper mapper = new ObjectMapper();
        JsonNode root = mapper.readTree(input);
        if (!root.has(ARGS))
            return null;
        JsonNode args = root.get(ARGS);
        if (!args.isObject())
            return null;
        if (!args.has(SCALE_ARGS))
            return null;
        JsonNode scaleArgs = args.get(SCALE_ARGS);
        if (!scaleArgs.isArray())
            return null;
        Scale scale = null;
        ArrayList<Dimension> dimensions = new ArrayList<Dimension>(scaleArgs.size() - 1);
        for (JsonNode dimension : scaleArgs) {
            String dimensionName = dimension.get(0).asText();
            String dimensionType = dimension.get(1).asText();
            if (dimensionType.equals(Scale.TYPE_NAME)) {
                scale = new Scale(dimension.get(2).asInt());
            } else if (dimensionType.equals(SetDimension.TYPE_NAME)) {
                ArrayList<String> values = new ArrayList<String>(dimension.get(2).size());
                for (JsonNode value : dimension.get(2)) {
                    values.add(Integer.toString(value.asInt()));
                }
                dimensions.add(new SetDimension(values));
            } else if (dimensionType.equals(RangeDimension.TYPE_NAME)) {
                JsonNode rangeData = dimension.get(2);
                dimensions.add(new RangeDimension(rangeData.get(0).asInt(), rangeData.get(1).asInt()));
            } else {
                throw new UnknownDimensionType();
            }
        }
        return new JobDescriptor(new Cube(dimensions, scale), root);
    }
}
