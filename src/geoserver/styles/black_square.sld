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
        <Name>base_adresse_nationale</Name>

        <UserStyle>
            <Title>base_adresse_nationale</Title>

            <FeatureTypeStyle>
                <Rule>
                    <Title>Single symbol</Title>

                    <PointSymbolizer>
                        <Graphic>
                            <Mark>
                                <WellKnownName>square</WellKnownName>

                                <Fill>
                                    <CssParameter name="fill">#000000</CssParameter>
                                </Fill>

                                <Stroke>
                                    <CssParameter name="stroke">#ffffff</CssParameter>
                                    <CssParameter name="stroke-width">1</CssParameter>
                                </Stroke>

                            </Mark>

                            <Size>6</Size>
                        </Graphic>
                    </PointSymbolizer>

                </Rule>
            </FeatureTypeStyle>
        </UserStyle>
    </NamedLayer>

</sld:StyledLayerDescriptor>