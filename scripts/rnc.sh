export INCLUDE_XSL=/home/thlw/a/schematron/trunk/schematron/code/iso_dsdl_include.xsl

export SCH_RNC=/home/thlw/a/schema/schematron.rnc
export SVRL_RNC=/home/thlw/a/schema/svrl.rnc

export SCH_SCH=/home/thlw/a/schema/schematron.sch
export SVRL_SCH=/home/thlw/a/schema/svrl.sch

xsltproc $INCLUDE_XSL main.sch > expanded.sch
