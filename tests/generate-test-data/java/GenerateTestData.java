import org.basex.core.Context;
import org.basex.query.QueryProcessor;

import org.yaml.snakeyaml.Yaml;

import java.io.FileInputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.List;
import java.util.Map;

public class GenerateTestData {

    public static void main(String[] args) throws Exception {
        Path repoRoot  = Paths.get("").toAbsolutePath();
        Path dataDir   = repoRoot.resolve("tests/data");
        Path targetDir = repoRoot.resolve("tests/target");

        System.out.println("Data dir:   " + dataDir);
        System.out.println("Target dir: " + targetDir);

        if (!Files.isDirectory(dataDir)) {
            System.err.println("ERROR: tests/data not found at " + dataDir);
            System.exit(1);
        }

        Yaml yaml = new Yaml();
        Context ctx = new Context();

        try (var stream = Files.list(dataDir)) {
            stream
                .filter(p -> p.toString().endsWith(".yml"))
                .sorted()
                .forEach(ymlPath -> {
                    String baseName = ymlPath.getFileName().toString()
                            .replaceAll("\\.yml$", "");
                    Path xmlPath = dataDir.resolve(baseName + ".xml");

                    if (!Files.exists(xmlPath)) {
                        System.err.println("WARNING: No matching XML for " + ymlPath.getFileName());
                        return;
                    }

                    try {
                        processFile(ctx, ymlPath, xmlPath, targetDir.resolve(baseName), baseName, yaml);
                    } catch (Exception e) {
                        System.err.println("ERROR processing " + baseName + ": " + e.getMessage());
                        e.printStackTrace();
                    }
                });
        }

        ctx.close();
        System.out.println("Done.");
    }

    @SuppressWarnings("unchecked")
    static void processFile(Context ctx, Path ymlPath, Path xmlPath,
                            Path outDir, String baseName, Yaml yaml) throws Exception {

        System.out.println("\nProcessing: " + baseName);

        List<Map<String, Object>> cases;
        try (var is = new FileInputStream(ymlPath.toFile())) {
            cases = yaml.load(is);
        }

        if (cases == null || cases.isEmpty()) {
            System.out.println("  (no test cases)");
            return;
        }

        Files.createDirectories(outDir);

        String absoluteXml = xmlPath.toAbsolutePath().toString().replace("\\", "/");
        String nsDeclarations = extractNamespaceDeclarations(ctx, absoluteXml);

        for (Map<String, Object> testCase : cases) {
            String id     = String.valueOf(testCase.get("id"));
            String xquery = (String) testCase.get("xquery");
            Path outFile  = outDir.resolve(id + ".xml");

            System.out.println("  id=" + id + "  xquery=" + (xquery == null || xquery.isBlank() ? "(none)" : xquery));

            String query;
            if (xquery == null || xquery.isBlank() || xquery.equals("()")) {
                query = nsDeclarations +
                        "file:write('" + esc(outFile) + "', doc('" + esc(absoluteXml) + "'))";
            } else {
                String mutation = xquery.replace("$doc", "$d");
                query =
                    "declare namespace file = 'http://expath.org/ns/file';\n" +
                    nsDeclarations +
                    "let $doc := doc('" + esc(absoluteXml) + "')\n" +
                    "let $result := copy $d := $doc modify (" + mutation + ") return $d\n" +
                    "return file:write('" + esc(outFile) + "', $result)";
            }

            try (QueryProcessor qp = new QueryProcessor(query, ctx)) {
                qp.value();
            }

            ensureTrailingNewline(outFile);

            System.out.println("    -> " + outFile);
        }
    }

    static String extractNamespaceDeclarations(Context ctx, String absoluteXml) throws Exception {
        String nsQuery =
            "for $ns in in-scope-prefixes(doc('" + esc(absoluteXml) + "')/*[1])\n" +
            "where $ns != 'xml'\n" +
            "return $ns || '=' || namespace-uri-for-prefix($ns, doc('" + esc(absoluteXml) + "')/*[1])";

        StringBuilder sb = new StringBuilder();
        try (QueryProcessor qp = new QueryProcessor(nsQuery, ctx)) {
            var iter = qp.iter();
            for (;;) {
                var item = iter.next();
                if (item == null) break;
                String pair = item.toJava().toString();
                int eq = pair.indexOf('=');
                if (eq < 0) continue;
                String prefix = pair.substring(0, eq);
                String uri    = pair.substring(eq + 1);
                sb.append("declare namespace ")
                  .append(prefix)
                  .append("='")
                  .append(uri)
                  .append("';\n");
            }
        }
        return sb.toString();
    }

    static void ensureTrailingNewline(Path file) throws Exception {
        byte[] content = Files.readAllBytes(file);
        if (content.length == 0 || content[content.length - 1] != '\n') {
            try (var out = Files.newOutputStream(file, StandardOpenOption.APPEND)) {
                out.write('\n');
            }
        }
    }

    static String esc(Path p) {
        return p.toAbsolutePath().toString().replace("\\", "/").replace("'", "\\'");
    }

    static String esc(String s) {
        return s.replace("'", "\\'");
    }
}
