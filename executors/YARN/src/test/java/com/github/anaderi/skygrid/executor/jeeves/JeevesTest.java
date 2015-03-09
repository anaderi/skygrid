package com.github.anaderi.skygrid.executor.jeeves;

import junit.framework.TestCase;

import java.util.HashMap;
import java.util.Map;

/**
 * Created by stromsund on 09.03.15.
 */
public class JeevesTest extends TestCase {
    public void testGenerateArguments() {
        Map<String, String> arguments = new HashMap<String, String>(3);
        arguments.put("--nEvents", "$DEFAULT_AMOUNT");
        arguments.put("--output", "$OUTPUT_DIR/root");
        arguments.put("--seed", "$JOB_ID");
        arguments.put("__POS", "--enable-logging");

        Map<String, String> substitutions = new HashMap<String, String>(10);
        substitutions.put("$USELESS", "abcdefg");
        substitutions.put("$JOB_ID", "101");
        substitutions.put("$OUTPUT_DIR", "/output");

        String command = Jeeves.generateArguments(arguments, substitutions);
        assertEquals(
            " --enable-logging --nEvents=$DEFAULT_AMOUNT" +
                " --seed=101 --output=/output/root",
            command);
    }
}
