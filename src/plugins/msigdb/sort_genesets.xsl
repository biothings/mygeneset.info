<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" indent="yes" />

     <xsl:template match="MSIGDB">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:apply-templates select="GENESET">
                <xsl:sort select="@ORGANISM" order="ascending"/>
            </xsl:apply-templates>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>