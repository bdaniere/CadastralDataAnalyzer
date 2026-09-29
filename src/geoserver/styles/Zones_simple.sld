<?xml version="1.0" encoding="UTF-8"?>
<sld:StyledLayerDescriptor
    version="1.0.0"
    xmlns="http://www.opengis.net/sld"
    xmlns:sld="http://www.opengis.net/sld"
    xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="
        http://www.opengis.net/sld
        http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd">

    <NamedLayer>
        <Name>parcelles</Name>

        <UserStyle>
            <Title>parcelles</Title>

            <FeatureTypeStyle>
                <Rule>
                    <Title>Single symbol</Title>

                    <PolygonSymbolizer>
                        <Fill>
                            <CssParameter name="fill-opacity">0</CssParameter>
                        </Fill>
                        <Stroke>
                            <CssParameter name="stroke">#000000</CssParameter>
                            <CssParameter name="stroke-width">0.5</CssParameter>
                            <CssParameter name="stroke-opacity">0.15</CssParameter>
                            <CssParameter name="stroke-linejoin">bevel</CssParameter>
                            <CssParameter name="stroke-linecap">square</CssParameter>
                        </Stroke>
                    </PolygonSymbolizer>

                </Rule>
            </FeatureTypeStyle>
        </UserStyle>
    </NamedLayer>

</sld:StyledLayerDescriptor>