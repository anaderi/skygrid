package com.github.anaderi.skygrid;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * This class implements JobDescriptor
 * https://github.com/anaderi/skygrid/wiki/Job-descriptor
 */
public class JobDescriptor {
    private static final String ARGS = "args";
    private static final String SCALE_ARGS = "scaleArg";

    private final Cube argsCube_;
    private final ObjectNode root_;

    public static class JobDescriptorFormatException extends Exception {}
    public static class UnknownDimensionType extends JobDescriptorFormatException {}
    public static class OnlyOneScaleArgumentIsPossible extends JobDescriptorFormatException {}
    public static class ScaleParamCanNotBeDistributed extends JobDescriptorFormatException {}

    JobDescriptor(Cube argsCube, ObjectNode root) {
        argsCube_ = argsCube;
        root_ = root;
    }

    public static JobDescriptor fromJsonString(String input) throws JobDescriptorFormatException, IOException {
        ObjectMapper mapper = new ObjectMapper();
        ObjectNode root = (ObjectNode)mapper.readTree(input);
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
        int scaleCount = -1;
        String scaleName = "";
        boolean wasScale = false;
        ArrayList<Dimension> dimensions = new ArrayList<Dimension>(scaleArgs.size() - 1);
        for (JsonNode dimension : scaleArgs) {
            String dimensionName = dimension.get(0).asText();
            String dimensionType = dimension.get(1).asText();
            if (dimensionType.equals(Scale.TYPE_NAME)) {
                if (wasScale)
                    throw new OnlyOneScaleArgumentIsPossible();
                wasScale = true;
                scaleName = dimensionName;
                scaleCount = dimension.get(2).asInt();
            } else if (dimensionType.equals(SetDimension.TYPE_NAME)) {
                ArrayList<String> values = new ArrayList<String>(dimension.get(2).size());
                for (JsonNode value : dimension.get(2)) {
                    values.add(Integer.toString(value.asInt()));
                }
                dimensions.add(new SetDimension(values, dimensionName));
            } else if (dimensionType.equals(RangeDimension.TYPE_NAME)) {
                JsonNode rangeData = dimension.get(2);
                dimensions.add(new RangeDimension(rangeData.get(0).asInt(), rangeData.get(1).asInt(), dimensionName));
            } else {
                throw new UnknownDimensionType();
            }
        }

        Scale scale;
        if (wasScale) {
            int volume = 1;
            for (Dimension d : dimensions) {
                volume *= d.length();
            }
            if (scaleCount % volume != 0)
                throw new ScaleParamCanNotBeDistributed();
            scale = new Scale(scaleCount / volume, scaleName);
        } else {
            scale = null;
        }
        Cube cube = new Cube(dimensions, scale);
        ((ObjectNode)root.get(ARGS)).remove(SCALE_ARGS);
        return new JobDescriptor(cube, root);
    }

    public static JsonNode convertCubeToJson(Cube cube) {
        ArrayNode result = new ArrayNode(JsonNodeFactory.instance);
        for (Dimension d : cube.dimensions()) {
            ArrayNode serializedDimension = new ArrayNode(JsonNodeFactory.instance);
            serializedDimension.add(d.name());
            serializedDimension.add(d.description());
            ArrayNode serializedDimensionsData = new ArrayNode(JsonNodeFactory.instance);
            for (Integer value : d.serialize()) {
                serializedDimensionsData.add(value);
            }
            serializedDimension.add(serializedDimensionsData);
            result.add(serializedDimension);
        }
        if (cube.scale() != null) {
            ArrayNode serializedScale = new ArrayNode(JsonNodeFactory.instance);
            serializedScale.add(cube.scale().name());
            serializedScale.add(cube.scale().description());

            // Scale argument of JobDescriptor shows total cube volume.
            serializedScale.add(cube.scale().length() * cube.volume());
            result.add(serializedScale);
        }
        return result;
    }

    public String toString() {
        ObjectNode tmp = root_.deepCopy();
        ((ObjectNode)tmp.get(ARGS)).set(SCALE_ARGS, convertCubeToJson(argsCube_));
        return tmp.toString();
    }

    List<JobDescriptor> split(int splitCount) throws Cube.ImpossibleToSplit {
        List<Cube> cubes = argsCube_.split(splitCount);
        ArrayList<JobDescriptor> result = new ArrayList<JobDescriptor>(splitCount);
        for (Cube cube : cubes) {
            result.add(new JobDescriptor(cube, root_.deepCopy()));
        }
        return result;
    }
}
