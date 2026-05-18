## Why use Saxon

Jeg forsøger at bruge pyschematron, men jeg er løbet ind i nogle
issues, hvor det er rart at kunne sammenligne med saxon behavior,
som er det tætteste vi kommer på en reference implementation for
schematron (og muligvis også for xsd).

## Hvad er Saxon

Et XML værktøj baseret på Java; kører i JVM. Træls at installere,
fx skal man selv lave en executable shell wrapper.

Maintaines af Saxonica. De frigiver tre forskellige versioner.
Saxon HE (home edition) er 100% open source. Saxon PE og EE
kræver licens. Saxon PE er fuldt ud tilstrækkeligt til alt,
hvad jeg skal bruge.

Manden bag projektet/firmaet er Michael Kay, som i øvrigt også
er en af de mest centrale personer bag XPath of XSLT standarderne.

## Install Saxon with apt

sudo apt install libsaxonhe-java

## Create a wrapper shell script:

mkdir -p ~/.local/bin
cat > ~/.local/bin/saxon <<'EOF'
#!/usr/bin/env bash
exec java -jar /usr/share/java/Saxon-HE.jar "$@"
EOF
chmod +x ~/.local/bin/saxon

## git clone schxslt

git clone https://codeberg.org/SchXslt/schxslt.git


## build schxslt

cd schxslt
mvn -pl cli -am package

## install schxslt

cd schxslt

mkdir -p ~/.local/bin

cat > ~/.local/bin/schxslt <<'EOF'
#!/usr/bin/env bash
exec java -jar /home/thlw/a/schxslt/cli/target/schxslt-cli.jar "$@"
EOF

chmod +x ~/.local/bin/schxslt


## Test with saxon

export SVRL=~/a/schxslt/core/target/xslt-only/2.0/compile-for-svrl.xsl

Now compile to no_comments.xsl:

```sh
saxon \
  -xsl:$SVRL \
  -s:no_comments.sch \
  -o:no_comments.xsl
```

```sh
saxon \
  -xsl:no_comments.xsl \
  -s:foo_with_comment.xml \
  -o:report.svrl
```

Now you can see the validation result in report.svrl.


# Test with schxslt

schxslt -s no_comments.sch -d foo_with_comment.xml
